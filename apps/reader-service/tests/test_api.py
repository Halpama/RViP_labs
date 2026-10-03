import pytest


async def create_reader(client, full_name="Ada Lovelace", card_number="CARD-1"):
    response = await client.post(
        "/readers",
        json={"full_name": full_name, "card_number": card_number},
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_empty_reader_list(client):
    response = await client.get("/readers")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,path,json",
    [
        ("get", "/readers/999", None),
        ("patch", "/readers/999", {"full_name": "Unknown"}),
        ("delete", "/readers/999", None),
        ("post", "/readers/999/revoke-card", None),
        ("post", "/readers/999/issue-book", {"book_title": "Unknown"}),
        ("post", "/readers/999/return-book", None),
    ],
)
async def test_reader_operations_return_404_for_unknown_id(client, method, path, json):
    request = getattr(client, method)
    response = await request(path, **({"json": json} if json is not None else {}))

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_partial_update_and_invalid_patch_does_not_change_reader(client):
    reader = await create_reader(client)

    updated = await client.patch(f"/readers/{reader['id']}", json={"full_name": "Grace Hopper"})
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Grace Hopper"
    assert updated.json()["card_number"] == reader["card_number"]

    for payload in (
        {"full_name": None},
        {"card_number": ""},
        {},
        {"card_active": False},
        {"book_title": "Forbidden"},
        {"unknown": "Forbidden"},
    ):
        response = await client.patch(f"/readers/{reader['id']}", json=payload)
        assert response.status_code == 422

    unchanged = await client.get(f"/readers/{reader['id']}")
    assert unchanged.status_code == 200
    assert unchanged.json()["full_name"] == "Grace Hopper"
    assert unchanged.json()["card_number"] == reader["card_number"]


@pytest.mark.asyncio
async def test_duplicate_card_number_conflicts_leave_readers_unchanged(client):
    first = await create_reader(client, card_number="CARD-1")
    second = await create_reader(client, full_name="Grace Hopper", card_number="CARD-2")

    duplicate_create = await client.post(
        "/readers",
        json={"full_name": "Duplicate", "card_number": first["card_number"]},
    )
    assert duplicate_create.status_code == 409

    duplicate_update = await client.patch(
        f"/readers/{second['id']}",
        json={"card_number": first["card_number"]},
    )
    assert duplicate_update.status_code == 409

    unchanged = await client.get(f"/readers/{second['id']}")
    assert unchanged.status_code == 200
    assert unchanged.json()["card_number"] == "CARD-2"


@pytest.mark.asyncio
async def test_circulation_conflicts_leave_reader_unchanged(client):
    reader = await create_reader(client)
    reader_id = reader["id"]

    revoked = await client.post(f"/readers/{reader_id}/revoke-card")
    assert revoked.status_code == 200
    inactive_issue = await client.post(
        f"/readers/{reader_id}/issue-book",
        json={"book_title": "Inactive"},
    )
    assert inactive_issue.status_code == 409
    assert (await client.get(f"/readers/{reader_id}")).json()["book_title"] is None

    active_reader = await create_reader(client, full_name="Alan Turing", card_number="CARD-2")
    active_id = active_reader["id"]
    issued = await client.post(f"/readers/{active_id}/issue-book", json={"book_title": "Algorithms"})
    assert issued.status_code == 200

    second_book = await client.post(f"/readers/{active_id}/issue-book", json={"book_title": "Compilers"})
    assert second_book.status_code == 409
    assert (await client.get(f"/readers/{active_id}")).json()["book_title"] == "Algorithms"

    revoke = await client.post(f"/readers/{active_id}/revoke-card")
    assert revoke.status_code == 409
    delete = await client.delete(f"/readers/{active_id}")
    assert delete.status_code == 409
    assert (await client.get(f"/readers/{active_id}")).status_code == 200

    returned = await client.post(f"/readers/{active_id}/return-book")
    assert returned.status_code == 200
    no_book_return = await client.post(f"/readers/{active_id}/return-book")
    assert no_book_return.status_code == 409
    assert (await client.get(f"/readers/{active_id}")).json()["book_title"] is None


@pytest.mark.asyncio
async def test_summary_for_empty_mixed_and_all_issued_datasets(client):
    empty = await client.get("/reports/summary")
    assert empty.status_code == 200
    assert empty.json() == {"total_readers": 0, "outstanding_books": 0}

    first = await create_reader(client)
    second = await create_reader(client, full_name="Grace Hopper", card_number="CARD-2")
    await client.post(f"/readers/{first['id']}/issue-book", json={"book_title": "Algorithms"})

    mixed = await client.get("/reports/summary")
    assert mixed.status_code == 200
    assert mixed.json() == {"total_readers": 2, "outstanding_books": 1}

    await client.post(f"/readers/{second['id']}/issue-book", json={"book_title": "Compilers"})
    all_issued = await client.get("/reports/summary")
    assert all_issued.status_code == 200
    assert all_issued.json() == {"total_readers": 2, "outstanding_books": 2}


@pytest.mark.asyncio
async def test_reader_lifecycle(client):
    reader = await create_reader(client)
    reader_id = reader["id"]

    issued = await client.post(f"/readers/{reader_id}/issue-book", json={"book_title": "Algorithms"})
    assert issued.status_code == 200

    blocked = await client.delete(f"/readers/{reader_id}")
    assert blocked.status_code == 409

    returned = await client.post(f"/readers/{reader_id}/return-book")
    assert returned.status_code == 200
    assert returned.json()["book_title"] is None

    revoked = await client.post(f"/readers/{reader_id}/revoke-card")
    assert revoked.status_code == 200
    assert revoked.json()["card_active"] is False

    deleted = await client.delete(f"/readers/{reader_id}")
    assert deleted.status_code == 204
