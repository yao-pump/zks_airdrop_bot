import requests
import json

def get_random_image():
    response = requests.get("https://api.unsplash.com/photos/random", headers={"Accept-Version": "v1", "Authorization": "Client-ID eZguh7dfdhPkEdKHF43kV6ERtvt4zI-1glOyaoyegQw"})
    data = json.loads(response.text)

    return data['urls']['full'], data['alt_description']

def send_url_request(url, method='GET', headers=None, params=None, data=None):
    if not headers:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
    try:
        response = requests.post(url, headers=headers, data=data)
        # response = requests.request(method, url, headers=headers, params=params, data=data)
        if response.status_code == 200:
            print("Got NFT info successfully!")
            return response.json()
        else:
            print(f"Failed to upload file. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error sending URL request: {e}")
        return None

# {"name":"pepe","attributes":[],"image":"https://mintsquare.sfo3.cdn.digitaloceanspaces.com/mintsquare/mintsquare/DVs4it1BqbXamu5P1LzVdJ_1683930338725226565.webp"}
def upload_image_to_url(image, target_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    try:
        response = requests.post(target_url, headers=headers, files={'file': image})
        if response.status_code == 200:
            print("File uploaded successfully!")
            return response
        else:
            print(f"Failed to upload file. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

if __name__ == '__main__':
    image_url, image_name = get_random_image()
    print(f"Image URL: {image_url}")
    print(f"Image Name: {image_name}")

    # send_request()
    # file_path = "/Users/yao/Downloads/_91408619_55df76d5-2245-41c1-8031-07a4da3f313f.jpg.webp"
    # upload_file_to_url(file_path, MINT_SQUARE_UPLOAD_URL)

