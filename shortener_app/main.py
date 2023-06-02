from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
import validators

from .db import create_new_db_url_object, get_active_url_by_key, get_url_by_secret_key, insert_new_url_record, update_visit_count
from . import schema, models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)


def raise_not_found(request: Request):
    message = f"URL '{request.url}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)


@app.get('/')
def read_root():
    return "Welcome to the URL Shortener app!"


@app.post("/url", response_model=schema.URLInfo)
def create_url(requestBody: schema.URLBase, db: Session = Depends(get_db)):
    if not validators.url(requestBody.target_url):
        raise_bad_request("Invalid URL")

    db_url = insert_new_url_record(db, requestBody.target_url)
    db_url.url = db_url.key
    db_url.admin_url = db_url.secret_key

    return db_url


@app.get("/all")
def get_all_urls(db: Session = Depends(get_db)):
    return db.query(models.URL).all()


@app.get("/{url_key}")
def forward_url_key(
    url_key: str,
    request: Request,
    db: Session = Depends(get_db)
):
    db_url = update_visit_count(db, url_key)

    if db_url:
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)


@app.get("/admin/getInfo/{secret_key}")
def get_url_admin(
    secret_key: str,
    request: Request,
    db: Session = Depends(get_db)
):
    db_url = get_url_by_secret_key(db, secret_key)

    if db_url:
        return db_url
    else:
        raise_not_found(request)


@app.post("/admin/toggleActive")
def deactivate_url(
    requestBody: schema.URLToggleActiveRequestBody,
    request: Request,
    db: Session = Depends(get_db)
):
    db_url = get_url_by_secret_key(db, requestBody.secret_key)

    if db_url:
        db_url.is_active = db_url.is_active ^ True
        db.commit()
        return {"message": f"URL successfully {'activated' if db_url.is_active else 'deactivated'}"}
    else:
        raise_not_found(request)


@app.delete("/admin/delete")
def delete_url(
    requestBody: schema.URLDeleteRequestBody,
    request: Request,
    db: Session = Depends(get_db)
):
    db_url = get_url_by_secret_key(db, requestBody.secret_key)

    if db_url:
        db.delete(db_url)
        db.commit()
        return {"message": "URL successfully deleted"}
    else:
        raise_not_found(request)
