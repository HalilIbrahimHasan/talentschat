tamamen web, Python + Flask + HTML/JS/CSS ile yapılabilir. “Slack + Google Drive paylaşım + highlights” gibi; üstüne video upload + like ekliyoruz.

1) Ürün Kapsamı (MVP + Sonra)
MVP (ilk sürüm)

Auth: kayıt / giriş, şifre reset (opsiyonel)

Workspaces / Channels

Workspace oluştur / katıl (invite link / kod)

Channel oluştur (public/private)

Chat

Kanal chat’i + DM (opsiyonel)

Emoji reaction (👍 😂 ❤️)

Mesaj highlight / pin

Link preview (basit: sadece title çekme opsiyonel)

Docs & Files

Dosya upload (pdf/docx/png/zip vs)

“Docs” sayfası: kanala göre listelenen paylaşımlar

Script / code snippet paylaşımı (kod bloğu, kopyala butonu)

Mobile-friendly UI

Responsive layout (sidebar collapse, bottom nav)

Video

Video upload (mp4/webm)

Video feed (kanal bazlı veya workspace feed)

Like / unlike

Basit yorum (opsiyonel)

v1.1 (kolay büyütme)

Mesaj arama (FTS)

Mentions (@user)

Read receipts / last seen (opsiyonel)

Notification badge (client polling ya da websocket event)

2) Kullanıcı Rolleri

Owner/Admin (workspace yönetir)

Member (kanal chat + paylaşım)

Guest (sadece belirli channel’lar, opsiyonel)

3) Teknoloji Seçimi (Flask ile “aktif chat”)

Backend: Flask

Realtime Chat: Flask-SocketIO (WebSocket)

Alternatif: polling (kolay ama “aktif” hissi daha az)

DB: PostgreSQL (prod) / SQLite (dev)

ORM: SQLAlchemy + Alembic migration

Auth: Flask-Login + werkzeug hash + CSRF

Frontend: Server-side templates (Jinja2) + vanilla JS

CSS: Tailwind (CDN) veya custom CSS (BEM)

Upload storage:

Dev: local /uploads

Prod: S3 (ileride)

4) Uygulama Modülleri (Repo Structure)

Aşırı kompleks yapmadan “blueprint” ile tertemiz:

app/
  __init__.py            # create_app, extensions
  config.py
  extensions.py          # db, login_manager, socketio, csrf
  models/
    user.py
    workspace.py
    channel.py
    message.py
    file.py
    video.py
    reaction.py
    highlight.py
  blueprints/
    auth/
      routes.py, forms.py
    workspaces/
      routes.py
    channels/
      routes.py
    chat/
      routes.py, sockets.py   # websocket events
    files/
      routes.py
    videos/
      routes.py
    api/
      routes.py              # JSON endpoints (likes, reactions, fetch)
  templates/
    layout.html
    auth/
    workspace/
    channel/
    video/
  static/
    css/
    js/
      chat.js
      uploads.js
      reactions.js
      highlights.js
      videos.js
  services/
    permissions.py
    upload_service.py
    preview_service.py
    search_service.py
  utils/
    ids.py, time.py
migrations/
run.py

5) Ana Sayfalar (UI Akışı)

/login, /register

/w/<workspace_slug>: workspace dashboard

/w/<workspace_slug>/c/<channel_slug>: channel ekranı

Sol: channel list

Orta: message stream

Sağ drawer: pinned/highlights + shared docs

/w/<workspace_slug>/docs: tüm paylaşımlar

/w/<workspace_slug>/videos: video feed

/v/<video_id>: video detail + yorum + like

Mobile UI

Sidebar → hamburger ile aç/kapa

Alt bar: Chat / Docs / Videos / Profile

Mesaj input sticky bottom

6) Realtime Chat Olayları (SocketIO Event Taslağı)

Client → Server

join_room (workspace+channel room)

send_message (text, attachments refs, reply_to)

add_reaction (message_id, emoji)

toggle_highlight (message_id)

typing (channel_id)

Server → Client

message_created

reaction_updated

highlight_updated

user_typing

presence_updated (opsiyonel)

7) Veri Modeli (Basit ama genişler)
Core

users: id, name, email, password_hash, avatar_url, created_at

workspaces: id, name, slug, owner_id, created_at

workspace_members: id, workspace_id, user_id, role, joined_at

Channels & Chat

channels: id, workspace_id, name, slug, is_private, created_by

channel_members: id, channel_id, user_id

messages: id, channel_id, user_id, content, content_html(optional), created_at, edited_at, reply_to_id(optional)

Reactions & Highlights

message_reactions: id, message_id, user_id, emoji, created_at (unique: message_id+user_id+emoji)

message_highlights: id, message_id, highlighted_by, created_at (unique: message_id+highlighted_by)

message_pins: id, channel_id, message_id, pinned_by, created_at

Files & Docs

files: id, workspace_id, channel_id, uploader_id, filename, mime, size, storage_key/path, created_at

snippets: id, channel_id, user_id, title, language, code, created_at

Videos

videos: id, workspace_id, channel_id(optional), uploader_id, title, description, storage_key/path, duration(optional), created_at

video_likes: id, video_id, user_id, created_at (unique: video_id+user_id)

video_comments: id, video_id, user_id, content, created_at

8) API + Routes (Minimum Set)
HTML Routes

GET /w/<ws>/c/<ch> channel page (SSR)

GET /w/<ws>/docs

GET /w/<ws>/videos

GET /v/<id>

JSON API (JS için)

GET /api/channels/<id>/messages?before=<ts>&limit=50

POST /api/messages (fallback if websocket down)

POST /api/messages/<id>/reactions

POST /api/messages/<id>/highlight

POST /api/videos/<id>/like

POST /api/upload (file/video; type param)

9) Upload & Güvenlik (Çok kritik)

Allowed mime whitelist (video: mp4/webm; docs: pdf/docx/txt; images: png/jpg)

Max size: (ör. doc 20MB, video 200MB)

Virus scan (ileride) / en azından “dangerous extensions” block

Private channel access check: her request’te permission

CSRF (formlarda), JWT şart değil (session cookie yeter)

Rate limit: login + upload (Flask-Limiter)

10) Performans & UX (Basit iyileştirmeler)

Mesajlar pagination (infinite scroll)

Upload progress bar (XHR)

Video için: basit <video controls> + server “range requests” (Flask static send_file ile mümkün)

DB index:

messages(channel_id, created_at)

videos(workspace_id, created_at)

likes(video_id, user_id unique)

11) Architecture Özeti (Cursor’a direkt yapıştırmalık)

Monolith Flask + Blueprints

Realtime: Flask-SocketIO rooms = ws:<id>:ch:<id>

DB: Postgres + SQLAlchemy

Storage: local → S3

UI: Jinja + vanilla JS (fetch + socket events) + responsive CSS

Entities: workspace/channel/message/file/video + reactions/highlights/likes

Permissions: service layer can_view_channel(user, channel) vb.

API: küçük JSON endpoints + SSR pages