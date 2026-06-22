# test file
import requests


def check_status(base_url):
    "check that the server is running"
    try:
        status_response = requests.get(f"{base_url}/")
        print(status_response.status_code)
        print(status_response.json())
    except requests.RequestException as e:
        print(f"An unexpected error has occured: {e}")


def post_new_scene(base_url):
    new_scene = {
        "scene_no": 1,
        "scene_desc": "Test scene",
        "is_finished": True,
        "is_rendered": True,
    }
    try:
        new_scene_response = requests.post(f"{base_url}/scenes", json=new_scene)
        print(new_scene_response.status_code)
    except requests.RequestException as e:
        print(f"An unexpected error has occured: {e}")


def invalid_post_new_scene(base_url):
    new_scene = {
        "scene_no": "Ten",
        "scene_desc": "Test scene",
        "is_finished": 15,
        "is_rendered": True,
    }
    try:
        new_scene_response = requests.post(f"{base_url}/scenes", json=new_scene)
        print(new_scene_response.status_code)
    except requests.RequestException as e:
        print(f"An unexpected error has occured: {e}")


def get_all_scenes(base_url):
    try:
        all_scenes_response = requests.get(f"{base_url}/scenes/all")
        print(all_scenes_response.status_code)
        print(all_scenes_response.json())
    except requests.RequestException as e:
        print(f"An unexpected error has occured: {e}")


def get_single_scene(base_url, num: int):
    try:
        single_scene_response = requests.get(f"{base_url}/scenes/{num}")
        print(single_scene_response.status_code)
        print(single_scene_response.json())
    except requests.RequestException as e:
        print(f"An unexpected error has occured: {e}")

if __name__ == "__main__":
    # check_status("http://127.0.0.1:8000")
    # post_new_scene("http://127.0.0.1:8000")
    # invalid_post_new_scene("http://127.0.0.1:8000")
    # get_all_scenes("http://127.0.0.1:8000")
    get_single_scene("http://127.0.0.1:8000", num= 6)

