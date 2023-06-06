import datetime

from model.resources.config import ModelResourceConfig

BASE_URL = f"http://localhost{ ModelResourceConfig.url_prefix}"


def test_get_item(client_with_credentials, sample_record, search_clear):
    non_existing = client_with_credentials.get(f"{BASE_URL}yjuykyukyuk")
    assert non_existing.status_code == 404

    get_response = client_with_credentials.get(f"{BASE_URL}{sample_record['id']}")
    assert get_response.status_code == 200
    assert get_response.json["metadata"] == sample_record["metadata"]


def test_create(
    client_with_credentials, client, sample_metadata_list, app, search_clear
):
    created_responses = []
    for sample_metadata_point in sample_metadata_list:
        created_responses.append(
            client_with_credentials.post(f"{BASE_URL}", json=sample_metadata_point)
        )
        with app.test_client() as unauth_client:
            unauth_response = unauth_client.post(
                f"{BASE_URL}", json=sample_metadata_point
            )
            assert unauth_response.status_code == 403
    assert all([new_response.status_code == 201 for new_response in created_responses])

    for sample_metadata_point, created_response in zip(
        sample_metadata_list, created_responses
    ):
        created_response_reread = client_with_credentials.get(
            f"{BASE_URL}{created_response.json['id']}"
        )
        assert created_response_reread.status_code == 200
        assert (
            created_response_reread.json["metadata"]
            == sample_metadata_point["metadata"]
        )


def test_listing(client_with_credentials, sample_records, search_clear):
    listing_response = client_with_credentials.get(BASE_URL)
    hits = listing_response.json["hits"]["hits"]
    assert len(hits) == 25


def test_update(
    client_with_credentials, sample_record, sample_metadata_list, search_clear
):
    non_existing = client_with_credentials.put(
        f"{BASE_URL}yjuykyukyuk", json=sample_metadata_list[15]
    )
    assert non_existing.status_code == 404

    old_record_read_response_json = client_with_credentials.get(
        f"{BASE_URL}{sample_record['id']}"
    ).json

    update_response = client_with_credentials.put(
        f"{BASE_URL}{sample_record['id']}", json=sample_metadata_list[2]
    )

    updated_record_read_response = client_with_credentials.get(
        f"{BASE_URL}{sample_record['id']}"
    )

    assert updated_record_read_response.status_code == 200
    assert update_response.status_code == 200
    assert updated_record_read_response.status_code == 200

    assert old_record_read_response_json["metadata"] == sample_record.metadata
    assert (
        update_response.json["metadata"]
        == sample_metadata_list[2]["metadata"]
        != old_record_read_response_json["metadata"]
    )
    assert (
        updated_record_read_response.json["metadata"]
        == sample_metadata_list[2]["metadata"]
    )
    assert (
        updated_record_read_response.json["revision_id"]
        == old_record_read_response_json["revision_id"] + 1
    )

    # test patch - 405 METHOD NOT ALLOWED
    # to make it work change create_url_rules in resource and allow jsonpatch in request_body_parsers in resource config
    # patch_response = client_with_credentials.patch(f"{BASE_URL}{sample_record['id']}",
    #                                                              json={"path": "/metadata/title",
    #                                                              "op": "replace",
    #                                                              "value": "UPDATED!"})


def test_delete(client_with_credentials, sample_record, app, search_clear):
    non_existing = client_with_credentials.delete(f"{BASE_URL}yjuykyukyuk")
    assert non_existing.status_code == 404

    read_response = client_with_credentials.get(f"{BASE_URL}{sample_record['id']}")
    assert read_response.status_code == 200

    with app.test_client() as unauth_client:
        unauth_delete_response = unauth_client.delete(
            f"{BASE_URL}{sample_record['id']}"
        )
        assert unauth_delete_response.status_code == 403

    delete_response = client_with_credentials.delete(f"{BASE_URL}{sample_record['id']}")
    assert delete_response.status_code == 204

    deleted_get_response = client_with_credentials.delete(
        f"{BASE_URL}{sample_record['id']}"
    )
    assert deleted_get_response.status_code == 410


def test_search(client_with_credentials, sample_records, search_clear):
    sample_record = sample_records[0]
    res_one = client_with_credentials.get(f"{BASE_URL}?q=fish attack painting")
    res_fail = client_with_credentials.get(f"{BASE_URL}?q=wefrtghthy")
    res_created = client_with_credentials.get(
        f"{BASE_URL}?q={str(datetime.datetime.now().date())}"
    )
    res_created_fail = client_with_credentials.get(f"{BASE_URL}?q=2022-10-16")
    res_facets = client_with_credentials.get(
        f"{BASE_URL}?created={sample_record.created.isoformat()}"
    )

    assert len(res_fail.json["hits"]["hits"]) == 0

    assert len(res_one.json["hits"]["hits"]) == 1
    assert len(res_created.json["hits"]["hits"]) == 25
    assert len(res_created_fail.json["hits"]["hits"]) == 0
    assert len(res_facets.json["hits"]["hits"]) == 1
