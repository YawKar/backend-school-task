# encoding=utf8

import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASEURL = "http://localhost:8080"

ROOT_ID = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"

def request(path, method="GET", data=None, json_response=False):
    try:
        params = {
            "url": f"{API_BASEURL}{path}",
            "method": method,
            "headers": {},
        }

        if data:
            params["data"] = json.dumps(
                data, ensure_ascii=False).encode("utf-8")
            params["headers"]["Content-Length"] = len(params["data"])
            params["headers"]["Content-Type"] = "application/json"

        req = urllib.request.Request(**params)

        with urllib.request.urlopen(req) as res:
            res_data = res.read().decode("utf-8")
            if json_response:
                res_data = json.loads(res_data)
            return (res.getcode(), res_data)
    except urllib.error.HTTPError as e:
        return (e.getcode(), None)


def deep_sort_children(node):
    if node.get("children"):
        node["children"].sort(key=lambda x: x["id"])

        for child in node["children"]:
            deep_sort_children(child)


def print_diff(expected, response):
    with open("expected.json", "w") as f:
        json.dump(expected, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    with open("response.json", "w") as f:
        json.dump(response, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    subprocess.run(["git", "--no-pager", "diff", "--no-index",
                    "expected.json", "response.json"])

def test_1():
    ### Imports one offer, then tries to get it, after that tries to delete it and get it again
    # import one offer
    OFFER_IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "Phone 12",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": None,
                "price": 79999
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=OFFER_IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    # get this offer
    EXPECTED_OFFER = {
        "type": "OFFER",
        "name": "Phone 12",
        "id": "863e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "children": None,
        "price": 79999,
        "date": "2022-02-03T15:00:00.000Z"
    }
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_OFFER)
    if response != EXPECTED_OFFER:
        print_diff(EXPECTED_OFFER, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    # delete this offer
    status, _ = request(f"/delete/863e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    # try to get this offer
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test 1 passed!")

def test_2():
    ### Imports one category, then tries to get it, then tries to delete it, then get it again
    # import one category
    CATEGORY_IMPORT = {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Phones",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3"
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=CATEGORY_IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    # get this category
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "Phones",
        "id": "863e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": None,
        "children": [],
        "date": "2022-02-03T15:00:00.000Z"
    }
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    # delete this category
    status, _ = request(f"/delete/863e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    # try to get this category
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test 2 passed!")

def test_3():
    ### Test:
    #   1. Imports one category
    #   2. Imports one offer that is a child of category from stage 1
    #   3. Gets offer
    #   4. Gets category
    #   5. Deletes offer
    #   6. (Tries to) Gets offer
    #   7. Gets category
    #   8. Deletes category
    #   9. (Tries to) Gets category

    #   1. Imports one category
    CATEGORY_IMPORT = {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Phones",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3"
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=CATEGORY_IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   2. Imports one offer that is a child of category from stage 1
    OFFER_IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "Phone 12",
                "id": "123e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3",
                "price": 79999
            }
        ],
        "updateDate": "2022-02-06T11:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=OFFER_IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   3. Gets offer
    EXPECTED_OFFER = {
        "type": "OFFER",
        "name": "Phone 12",
        "id": "123e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": "863e1a7a-1304-42ae-943b-179184c077e3",
        "children": None,
        "price": 79999,
        "date": "2022-02-06T11:00:00.000Z"
    }
    status, response = request(f"/nodes/123e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_OFFER)
    if response != EXPECTED_OFFER:
        print_diff(EXPECTED_OFFER, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    #   4. Gets category
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "Phones",
        "id": "863e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": 79999,
        "children": [
            {
                "type": "OFFER",
                "name": "Phone 12",
                "id": "123e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3",
                "price": 79999,
                "children": None,
                "date": "2022-02-06T11:00:00.000Z"
            }
        ],
        "date": "2022-02-06T11:00:00.000Z"
    }
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    #   5. Deletes offer
    status, _ = request(f"/delete/123e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   6. (Tries to) Gets offer
    status, response = request(f"/nodes/123e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    #   7. Gets category
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "Phones",
        "id": "863e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": None,
        "children": [],
        "date": "2022-02-06T11:00:00.000Z"
    }
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    #   8. Deletes category
    status, _ = request(f"/delete/863e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   9. (Tries to) Gets category
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test 3 passed!")

def test_4():
    ### Test:
    #   1.  Imports one category with two child offers
    #   2.  Gets category
    #   3.  Deletes one child
    #   4.  Gets category
    #   5.  Deletes another child
    #   6.  Gets category
    #   7.  Deletes category
    #   8.  (Tries to) get category

    #   1.  Imports one category with two childs offer
    IMPORT = {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Phones",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3"
            },
            {
                "type": "OFFER",
                "name": "Phone 1",
                "id": "113e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4000,
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3"
            },
            {
                "type": "OFFER",
                "name": "Phone 2",
                "id": "223e1a7a-1304-42ae-943b-179184c077e3",
                "price": 8200,
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3"
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   2.  Gets category
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "Phones",
        "id": "863e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": 6100,
        "children": [
            {
                "type": "OFFER",
                "name": "Phone 1",
                "id": "113e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4000,
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3",
                "children": None,
                "date": "2022-02-03T15:00:00.000Z"
            },
            {
                "type": "OFFER",
                "name": "Phone 2",
                "id": "223e1a7a-1304-42ae-943b-179184c077e3",
                "price": 8200,
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3",
                "children": None,
                "date": "2022-02-03T15:00:00.000Z"
            }
        ],
        "date": "2022-02-03T15:00:00.000Z"
    }
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    #   3.  Deletes one child
    status, _ = request(f"/delete/223e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   4.  Gets category
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "Phones",
        "id": "863e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": 4000,
        "children": [
            {
                "type": "OFFER",
                "name": "Phone 1",
                "id": "113e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4000,
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3",
                "children": None,
                "date": "2022-02-03T15:00:00.000Z"
            }
        ],
        "date": "2022-02-03T15:00:00.000Z"
    }
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    #   5.  Deletes another child
    status, _ = request(f"/delete/113e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   6.  Gets category
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "Phones",
        "id": "863e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": None,
        "children": [],
        "date": "2022-02-03T15:00:00.000Z"
    }
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    #   7.  Deletes category
    status, _ = request(f"/delete/863e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   8.  (Tries to) get category
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test 4 passed!")

def test_5():
    ### Test:
    #   1.  Imports one category with two child offers
    #   2.  Imports the same category again with another name
    #   3.  Gets the category
    #   4.  Deletes the category
    #   5.  (Tries to) Get category
    #   6.  (Tries to) Get first child
    #   7.  (Tries to) Get second child

    #   1.  Imports one category with two childs offer
    IMPORT = {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Phones",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3"
            },
            {
                "type": "OFFER",
                "name": "Phone 1",
                "id": "113e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4000,
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3"
            },
            {
                "type": "OFFER",
                "name": "Phone 2",
                "id": "223e1a7a-1304-42ae-943b-179184c077e3",
                "price": 8200,
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3"
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   2.  Imports the same category again with another name
    IMPORT = {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Laptops",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3"
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   3.  Gets the category
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "Laptops",
        "id": "863e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": 6100,
        "children": [
            {
                "type": "OFFER",
                "name": "Phone 1",
                "id": "113e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4000,
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3",
                "children": None,
                "date": "2022-02-03T15:00:00.000Z"
            },
            {
                "type": "OFFER",
                "name": "Phone 2",
                "id": "223e1a7a-1304-42ae-943b-179184c077e3",
                "price": 8200,
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3",
                "children": None,
                "date": "2022-02-03T15:00:00.000Z"
            }
        ],
        "date": "2022-02-03T15:00:00.000Z"
    }
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    #   4.  Deletes the category
    status, _ = request(f"/delete/863e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   5.  (Tries to) Get category
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    #   6.  (Tries to) Get first child
    status, response = request(f"/nodes/113e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    #   7.  (Tries to) Get second child
    status, response = request(f"/nodes/223e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test 5 passed!")

def test_6():
    ### Test:
    #   1.  Tries to delete shop unit that doesn't exist

    #   1.  Tries to delete shop unit that doesn't exist
    status, _ = request(f"/delete/863e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test 6 passed!")

def test_7():
    ### Test:
    #   1.  Imports one offer which date's not between selected startTime and endTime
    #   2.  Tries to get sales and check if it is empty
    #   3.  Deletes this offer
    #   4.  Tries to get this offer

    #   1.  Imports one offer which date's not between selected startTime and endTime
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "Phone 13",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "price": 1231,
                "parentId": None
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   2.  Tries to get sales and check if it is empty
    params = urllib.parse.urlencode({
        "date": "2022-02-03T14:59:59.000Z"
    })
    status, response = request(f"/sales?{params}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    EXPECTED_SALES = {
        "items": []
    }
    deep_sort_children(response)
    deep_sort_children(EXPECTED_SALES)
    if response != EXPECTED_SALES:
        print_diff(EXPECTED_SALES, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    #   3.  Deletes this offer
    status, _ = request(f"/delete/863e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   4.  Tries to get this offer
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test 7 passed!")

def test_8():
    ### Test:
    #   1.  Imports one offer which date is between selected startTime and endTime (endTime case)
    #   2.  Tries to get sales and check if it contains offer
    #   3.  Deletes this offer
    #   4.  Tries to get this offer

    #   1.  Imports one offer which date is between selected startTime and endTime
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "Phone 13",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "price": 1231,
                "parentId": None
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   2.  Tries to get sales and check if it is empty
    params = urllib.parse.urlencode({
        "date": "2022-02-03T15:00:00.000Z"
    })
    status, response = request(f"/sales?{params}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    EXPECTED_SALES = {
        "items": [
            {
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "name": "Phone 13",
                "date": "2022-02-03T15:00:00.000Z",
                "parentId": None,
                "children": None,
                "price": 1231,
                "type": "OFFER"
            }
        ]
    }
    deep_sort_children(response)
    deep_sort_children(EXPECTED_SALES)
    if response != EXPECTED_SALES:
        print_diff(EXPECTED_SALES, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    #   3.  Deletes this offer
    status, _ = request(f"/delete/863e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   4.  Tries to get this offer
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test 8 passed!")

def test_9():
    ### Test:
    #   1.  Imports one offer which date is between selected startTime and endTime (startTime case)
    #   2.  Tries to get sales and check if it contains offer
    #   3.  Deletes this offer
    #   4.  Tries to get this offer

    #   1.  Imports one offer which date is between selected startTime and endTime
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "Phone 13",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "price": 1231,
                "parentId": None
            }
        ],
        "updateDate": "2022-02-02T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   2.  Tries to get sales and check if it is empty
    params = urllib.parse.urlencode({
        "date": "2022-02-03T15:00:00.000Z"
    })
    status, response = request(f"/sales?{params}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    EXPECTED_SALES = {
        "items": [
            {
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "name": "Phone 13",
                "date": "2022-02-02T15:00:00.000Z",
                "parentId": None,
                "price": 1231,
                "children": None,
                "type": "OFFER"
            }
        ]
    }
    deep_sort_children(response)
    deep_sort_children(EXPECTED_SALES)
    if response != EXPECTED_SALES:
        print_diff(EXPECTED_SALES, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    #   3.  Deletes this offer
    status, _ = request(f"/delete/863e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   4.  Tries to get this offer
    status, response = request(f"/nodes/863e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test 9 passed!")

def test_10():
    ### Test:
    #   1.  Imports three offers with dates between selected startTime and endTime (startTime, ~middleTime and endTime cases)
    #   2.  Tries to get sales and check if it contains offers
    #   3.  Deletes these offers
    #   4.  Tries to get these offers

    #   1.  Imports three offers with dates between selected startTime and endTime (startTime, ~middleTime and endTime cases)
    #   1.1  Imports first offer with startTime
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "Phone 13",
                "id": "163e1a7a-1304-42ae-943b-179184c077e3",
                "price": 1231,
                "parentId": None
            }
        ],
        "updateDate": "2022-02-02T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   1.2  Imports second offer with ~middleTime
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "Phone 14",
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": 1111,
                "parentId": None
            }
        ],
        "updateDate": "2022-02-03T07:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   1.3  Imports third offer with endTime
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "Phone 15",
                "id": "363e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4553,
                "parentId": None
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   2.  Tries to get sales and check if it contains offers
    params = urllib.parse.urlencode({
        "date": "2022-02-03T15:00:00.000Z"
    })
    status, response = request(f"/sales?{params}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    EXPECTED_SALES = {
        "items": [
            {
                "id": "163e1a7a-1304-42ae-943b-179184c077e3",
                "name": "Phone 13",
                "date": "2022-02-02T15:00:00.000Z",
                "parentId": None,
                "price": 1231,
                "children": None,
                "type": "OFFER"
            },
            {
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "name": "Phone 14",
                "date": "2022-02-03T07:00:00.000Z",
                "parentId": None,
                "price": 1111,
                "children": None,
                "type": "OFFER"
            },
            {
                "id": "363e1a7a-1304-42ae-943b-179184c077e3",
                "name": "Phone 15",
                "date": "2022-02-03T15:00:00.000Z",
                "parentId": None,
                "price": 4553,
                "children": None,
                "type": "OFFER"
            }
        ]
    }
    deep_sort_children(response)
    deep_sort_children(EXPECTED_SALES)
    if response != EXPECTED_SALES:
        print_diff(EXPECTED_SALES, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)

    #   3.  Deletes these offers
    status, _ = request(f"/delete/163e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    status, _ = request(f"/delete/263e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    status, _ = request(f"/delete/363e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"

    #   4.  Tries to get these offers
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"
    status, response = request(f"/nodes/263e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"
    status, response = request(f"/nodes/363e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test 10 passed!")

def test_11():
    ### Test:
    #   1.  Imports category CATEGORY_1
    #   2.  Imports category CATEGORY_2 with parentId of CATEGORY_1 and new date
    #   3.  Gets CATEGORY_1
    #   4.  Imports offer OFFER_1 with parentId of CATEGORY_2 and new date
    #   5.  Gets CATEGORY_1
    #   6.  Imports offer OFFER_2 with parentId of CATEGORY_1 and new date
    #   7.  Gets CATEGORY_1
    #   8.  Imports offer OFFER_3 with parentId of CATEGORY_2 and new date
    #   9.  Gets CATEGORY_1
    #   10. Imports offer OFFER_4 with parentId of CATEGORY_1 and new date
    #   11. Gets CATEGORY_1
    #   12. Deletes OFFER_1
    #   13. Gets CATEGORY_1
    #   14. Deletes OFFER_2
    #   15. Gets CATEGORY_1
    #   16. Deletes OFFER_3
    #   17. Gets CATEGORY_1
    #   18. Deletes OFFER_4
    #   19. Gets CATEGORY_1
    #   20. Deletes CATEGORY_2
    #   21. Gets CATEGORY_1
    #   22. Deletes CATEGORY_1
    #   23. (Tries to) Gets CATEGORY_1

    #   1.  Imports category CATEGORY_1
    IMPORT = {
        "items": [
            {
                "type": "CATEGORY",
                "name": "CATEGORY_1",
                "id": "163e1a7a-1304-42ae-943b-179184c077e3"
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   2.  Imports category CATEGORY_2 with parentId of CATEGORY_1 and new date
    IMPORT = {
        "items": [
            {
                "type": "CATEGORY",
                "name": "CATEGORY_2",
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3"
            }
        ],
        "updateDate": "2022-02-04T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   3.  Gets CATEGORY_1
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "CATEGORY_1",
        "id": "163e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": None,
        "date": "2022-02-04T15:00:00.000Z",
        "children": [
            {
                "type": "CATEGORY",
                "name": "CATEGORY_2",
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": None,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "children": [],
                "date": "2022-02-04T15:00:00.000Z"
            }
        ]
    }
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)
    #   4.  Imports offer OFFER_1 with parentId of CATEGORY_2 and new date
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "OFFER_1",
                "id": "363e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": 1234
            }
        ],
        "updateDate": "2022-02-05T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   5.  Gets CATEGORY_1
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "CATEGORY_1",
        "id": "163e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": 1234,
        "date": "2022-02-05T15:00:00.000Z",
        "children": [
            {
                "type": "CATEGORY",
                "name": "CATEGORY_2",
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": 1234,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-05T15:00:00.000Z",
                "children": [
                    {
                        "type": "OFFER",
                        "name": "OFFER_1",
                        "id": "363e1a7a-1304-42ae-943b-179184c077e3",
                        "parentId": "263e1a7a-1304-42ae-943b-179184c077e3",
                        "price": 1234,
                        "children": None,
                        "date": "2022-02-05T15:00:00.000Z"
                    }
                ]
            }
        ]
    }
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)
    #   6.  Imports offer OFFER_2 with parentId of CATEGORY_1 and new date
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "OFFER_2",
                "id": "463e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "price": 7777
            }
        ],
        "updateDate": "2022-02-06T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   7.  Gets CATEGORY_1
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "CATEGORY_1",
        "id": "163e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": 4505,
        "date": "2022-02-06T15:00:00.000Z",
        "children": [
            {
                "type": "OFFER",
                "name": "OFFER_2",
                "id": "463e1a7a-1304-42ae-943b-179184c077e3",
                "price": 7777,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-06T15:00:00.000Z",
                "children": None
            },
            {
                "type": "CATEGORY",
                "name": "CATEGORY_2",
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": 1234,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-05T15:00:00.000Z",
                "children": [
                    {
                        "type": "OFFER",
                        "name": "OFFER_1",
                        "id": "363e1a7a-1304-42ae-943b-179184c077e3",
                        "parentId": "263e1a7a-1304-42ae-943b-179184c077e3",
                        "price": 1234,
                        "children": None,
                        "date": "2022-02-05T15:00:00.000Z"
                    }
                ]
            }
        ]
    }
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)
    #   8.  Imports offer OFFER_3 with parentId of CATEGORY_2 and new date
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "OFFER_3",
                "id": "563e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": 6385
            }
        ],
        "updateDate": "2022-02-07T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   9.  Gets CATEGORY_1
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "CATEGORY_1",
        "id": "163e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": 5132,
        "date": "2022-02-07T15:00:00.000Z",
        "children": [
            {
                "type": "OFFER",
                "name": "OFFER_2",
                "id": "463e1a7a-1304-42ae-943b-179184c077e3",
                "price": 7777,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-06T15:00:00.000Z",
                "children": None
            },
            {
                "type": "CATEGORY",
                "name": "CATEGORY_2",
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": 3809,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-07T15:00:00.000Z",
                "children": [
                    {
                        "type": "OFFER",
                        "name": "OFFER_1",
                        "id": "363e1a7a-1304-42ae-943b-179184c077e3",
                        "parentId": "263e1a7a-1304-42ae-943b-179184c077e3",
                        "price": 1234,
                        "children": None,
                        "date": "2022-02-05T15:00:00.000Z"
                    },
                    {
                        "type": "OFFER",
                        "name": "OFFER_3",
                        "id": "563e1a7a-1304-42ae-943b-179184c077e3",
                        "parentId": "263e1a7a-1304-42ae-943b-179184c077e3",
                        "price": 6385,
                        "children": None,
                        "date": "2022-02-07T15:00:00.000Z"
                    }
                ]
            }
        ]
    }
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)
    #   10. Imports offer OFFER_4 with parentId of CATEGORY_1 and new date
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "OFFER_4",
                "id": "663e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4391
            }
        ],
        "updateDate": "2022-02-08T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   11. Gets CATEGORY_1
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "CATEGORY_1",
        "id": "163e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": 4946,
        "date": "2022-02-08T15:00:00.000Z",
        "children": [
            {
                "type": "OFFER",
                "name": "OFFER_4",
                "id": "663e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4391,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-08T15:00:00.000Z",
                "children": None
            },
            {
                "type": "OFFER",
                "name": "OFFER_2",
                "id": "463e1a7a-1304-42ae-943b-179184c077e3",
                "price": 7777,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-06T15:00:00.000Z",
                "children": None
            },
            {
                "type": "CATEGORY",
                "name": "CATEGORY_2",
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": 3809,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-07T15:00:00.000Z",
                "children": [
                    {
                        "type": "OFFER",
                        "name": "OFFER_1",
                        "id": "363e1a7a-1304-42ae-943b-179184c077e3",
                        "parentId": "263e1a7a-1304-42ae-943b-179184c077e3",
                        "price": 1234,
                        "children": None,
                        "date": "2022-02-05T15:00:00.000Z"
                    },
                    {
                        "type": "OFFER",
                        "name": "OFFER_3",
                        "id": "563e1a7a-1304-42ae-943b-179184c077e3",
                        "parentId": "263e1a7a-1304-42ae-943b-179184c077e3",
                        "price": 6385,
                        "children": None,
                        "date": "2022-02-07T15:00:00.000Z"
                    }
                ]
            }
        ]
    }
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)
    #   12. Deletes OFFER_1
    status, _ = request(f"/delete/363e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   13. Gets CATEGORY_1
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "CATEGORY_1",
        "id": "163e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": 6184,
        "date": "2022-02-08T15:00:00.000Z",
        "children": [
            {
                "type": "OFFER",
                "name": "OFFER_4",
                "id": "663e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4391,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-08T15:00:00.000Z",
                "children": None
            },
            {
                "type": "OFFER",
                "name": "OFFER_2",
                "id": "463e1a7a-1304-42ae-943b-179184c077e3",
                "price": 7777,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-06T15:00:00.000Z",
                "children": None
            },
            {
                "type": "CATEGORY",
                "name": "CATEGORY_2",
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": 6385,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-07T15:00:00.000Z",
                "children": [
                    {
                        "type": "OFFER",
                        "name": "OFFER_3",
                        "id": "563e1a7a-1304-42ae-943b-179184c077e3",
                        "parentId": "263e1a7a-1304-42ae-943b-179184c077e3",
                        "price": 6385,
                        "children": None,
                        "date": "2022-02-07T15:00:00.000Z"
                    }
                ]
            }
        ]
    }
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)
    #   14. Deletes OFFER_2
    status, _ = request(f"/delete/463e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   15. Gets CATEGORY_1
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "CATEGORY_1",
        "id": "163e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": 5388,
        "date": "2022-02-08T15:00:00.000Z",
        "children": [
            {
                "type": "OFFER",
                "name": "OFFER_4",
                "id": "663e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4391,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-08T15:00:00.000Z",
                "children": None
            },
            {
                "type": "CATEGORY",
                "name": "CATEGORY_2",
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": 6385,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-07T15:00:00.000Z",
                "children": [
                    {
                        "type": "OFFER",
                        "name": "OFFER_3",
                        "id": "563e1a7a-1304-42ae-943b-179184c077e3",
                        "parentId": "263e1a7a-1304-42ae-943b-179184c077e3",
                        "price": 6385,
                        "children": None,
                        "date": "2022-02-07T15:00:00.000Z"
                    }
                ]
            }
        ]
    }
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)
    #   16. Deletes OFFER_3
    status, _ = request(f"/delete/563e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   17. Gets CATEGORY_1
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "CATEGORY_1",
        "id": "163e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": 4391,
        "date": "2022-02-08T15:00:00.000Z",
        "children": [
            {
                "type": "OFFER",
                "name": "OFFER_4",
                "id": "663e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4391,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-08T15:00:00.000Z",
                "children": None
            },
            {
                "type": "CATEGORY",
                "name": "CATEGORY_2",
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": None,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-07T15:00:00.000Z",
                "children": []
            }
        ]
    }
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)
    #   18. Deletes OFFER_4
    status, _ = request(f"/delete/663e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   19. Gets CATEGORY_1
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "CATEGORY_1",
        "id": "163e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": None,
        "date": "2022-02-08T15:00:00.000Z",
        "children": [
            {
                "type": "CATEGORY",
                "name": "CATEGORY_2",
                "id": "263e1a7a-1304-42ae-943b-179184c077e3",
                "price": None,
                "parentId": "163e1a7a-1304-42ae-943b-179184c077e3",
                "date": "2022-02-07T15:00:00.000Z",
                "children": []
            }
        ]
    }
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)
    #   20. Deletes CATEGORY_2
    status, _ = request(f"/delete/263e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   21. Gets CATEGORY_1
    EXPECTED_CATEGORY = {
        "type": "CATEGORY",
        "name": "CATEGORY_1",
        "id": "163e1a7a-1304-42ae-943b-179184c077e3",
        "parentId": None,
        "price": None,
        "date": "2022-02-08T15:00:00.000Z",
        "children": []
    }
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    deep_sort_children(response)
    deep_sort_children(EXPECTED_CATEGORY)
    if response != EXPECTED_CATEGORY:
        print_diff(EXPECTED_CATEGORY, response)
        print("Response tree doesn't match expected tree.")
        sys.exit(1)
    #   22. Deletes CATEGORY_1
    status, _ = request(f"/delete/163e1a7a-1304-42ae-943b-179184c077e3", method="DELETE")
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    #   23. (Tries to) Gets CATEGORY_1
    status, response = request(f"/nodes/163e1a7a-1304-42ae-943b-179184c077e3", json_response=True)
    assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test 11 passed!")

def json_schema_test_1():
    ### Test:
    #   1.  Tries to get information about node via incorrect UUID

    #   1.  Tries to get information about node via incorrect UUID
    status, response = request(f"/nodes/abcdefg", json_response=True)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    # length of the last 'word' of UUID doesn't equal to 12 (equals to 11)
    status, response = request(f"/nodes/223e1a7a-1304-42ae-943b-179184c077e", json_response=True)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    # length of the last 'word' of UUID doesn't equal to 12 (equals to 13)
    status, response = request(f"/nodes/223e1a7a-1304-42ae-943b-179184c077eca", json_response=True)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    print("Json Schema Test 1 passed!")

def json_schema_test_2():
    ### Test:
    #   1.  Tries to delete a node via incorrect UUID

    #   1.  Tries to delete a node via incorrect UUID
    status, response = request(f"/delete/abcdefg", method="DELETE")
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    # length of the last 'word' of UUID doesn't equal to 12 (equals to 11)
    status, response = request(f"/delete/223e1a7a-1304-42ae-943b-179184c077e", method="DELETE")
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    # length of the last 'word' of UUID doesn't equal to 12 (equals to 13)
    status, response = request(f"/delete/223e1a7a-1304-42ae-943b-179184c077eca", method="DELETE")
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    print("Json Schema Test 2 passed!")

def json_schema_test_3():
    ### Test:
    #   1.  Tries to import wrong request

    #   1.  Tries to import wrong request
    #   "name" contains 'integer' instead of 'string'
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": 123,
                "id": "113e1a7a-1304-42ae-943b-179184c077e3",
                "price": 4000,
                "parentId": None
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    #   "price" contains 'string' instead of 'integer'
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "kek",
                "id": "113e1a7a-1304-42ae-943b-179184c077e3",
                "price": "asdaa",
                "parentId": None
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    #   "id" doesn't look like UUID :)
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "kek",
                "id": "some-unknown-code",
                "price": 123,
                "parentId": None
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    #   "type" contains something else than a value from ["OFFER", "CATEGORY"]
    IMPORT = {
        "items": [
            {
                "type": "myOwnType",
                "name": "kek",
                "id": "113e1a7a-1304-42ae-943b-179184c077e3",
                "price": 123,
                "parentId": None
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    #   "parentId" has a type of 'number' but 'string' with UUID pattern required
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "kek",
                "id": "113e1a7a-1304-42ae-943b-179184c077e3",
                "price": 123,
                "parentId": 123
            }
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    #   "updateDate" contains wrong date (must be ISO 8601 formatted)
    IMPORT = {
        "items": [
            {
                "type": "OFFER",
                "name": "kek",
                "id": "113e1a7a-1304-42ae-943b-179184c077e3",
                "price": 123,
                "parentId": None
            }
        ],
        "updateDate": "2022-02-03 15:00"
    }
    status, _ = request("/imports", method="POST", data=IMPORT)
    assert status == 400, f"Expected HTTP status code 400, got {status}"

    print("Json Schema Test 3 passed!")


def functionality_tests():
    test_1()
    test_2()
    test_3()
    test_4()
    test_5()
    test_6()
    test_7()
    test_8()
    test_9()
    test_10()
    test_11()

def json_schema_tests():
    json_schema_test_1()
    json_schema_test_2()
    json_schema_test_3()

def test_all():
    functionality_tests()
    json_schema_tests()

def main():
    global API_BASEURL
    test_name = None

    for arg in sys.argv[1:]:
        if re.match(r"^https?://", arg):
            API_BASEURL = arg
        elif test_name is None:
            test_name = arg

    if API_BASEURL.endswith('/'):
        API_BASEURL = API_BASEURL[:-1]

    if test_name is None:
        test_all()
    else:
        test_func = globals().get(f"test_{test_name}")
        if not test_func:
            print(f"Unknown test: {test_name}")
            sys.exit(1)
        test_func()


if __name__ == "__main__":
    main()
