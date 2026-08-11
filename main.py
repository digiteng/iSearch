from fastapi import FastAPI, HTTPException
import niquests
INSTAGRAM_COOKIE = os.getenv("INSTAGRAM_COOKIE", "")

app = FastAPI()

HEADERS = {
	'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)',
	'x-ig-app-id': '936619743392459',
	'cookie': INSTAGRAM_COOKIE,
}

@app.get("/")
def read_root():
	return {"status": "FastAPI Vercel üzerinde çalışıyor!"}

@app.get("/search")
def search(user: str):
	if not user:
		raise HTTPException(status_code=400, detail="Kullanıcı adı belirtilmedi.")
		
	url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={user}"
	
	try:

		r = niquests.get(url, headers=HEADERS)

		if r.status_code != 200:
			raise HTTPException(status_code=r.status_code, detail=f"Instagram API hatası: {r.status_code}")
			
		return r.json()
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
