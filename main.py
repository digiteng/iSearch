import os
from fastapi import FastAPI, HTTPException, Header
import niquests

app = FastAPI()

VERCEL_API_KEY = os.getenv("MAC_0", "")
INSTA_URL = os.getenv("insta_url", "")
HEADERS = {
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)',
    'x-ig-app-id': '936619743392459',
}

@app.get("/")
def read_root():
    return {"status": " is working!"}

@app.get("/search")
def search(user: str, x_api_key: str = Header(None)):

    if not x_api_key or x_api_key != VERCEL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized access! Invalid API token.")

    if not user:
        raise HTTPException(status_code=400, detail="No username was specified.")
    url = f"{INSTA_URL}{user}"
    try:
        r = niquests.get(url, headers=HEADERS)

        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=f"Instagram API error: {r.status_code}")
            
        instagram_data = r.json()
        user_info = instagram_data.get("data", {}).get("user", {})
        
        if not user_info:
            return {"message: User not found or profile is private."}

        clean_profile = {
            "user_name": user_info.get("username"),
            "full_name": user_info.get("full_name"),
            "biography": user_info.get("biography"),
            "followed": user_info.get("edge_followed_by", {}).get("count", 0),
            "following": user_info.get("edge_follow", {}).get("count", 0),
            "profile_pic": user_info.get("profile_pic_url_hd"),
            "media_count": user_info.get("edge_owner_to_timeline_media", {}).get("count", 0)
        }

        reels_list = []
        posts = user_info.get("edge_owner_to_timeline_media", {}).get("edges", [])
        
        for post in posts:
            node = post.get("node", {})
            if node.get("__typename") == "GraphVideo" or node.get("is_video") is True:
                video_info = {
                    "id": node.get("id"),
                    "shortcode_id": node.get("shortcode"),
                    "url": f"https://instagram.com{node.get('shortcode')}/",
                    "video_url": node.get("video_url"), # Doğrudan mp4 linki
                    "view_count": node.get("video_view_count", 0),
                    "liked": node.get("edge_liked_by", {}).get("count", 0),
                    "desc": node.get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text", "") if node.get("edge_media_to_caption", {}).get("edges") else "",
                    "thumbnail": node.get("display_url")
                }
                reels_list.append(video_info)

        return {
            "profil": clean_profile,
            "reels": reels_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
