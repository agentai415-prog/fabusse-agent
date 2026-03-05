from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests, os, json

app = Flask(__name__)
CORS(app, origins="*")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")

# In-memory model store — persists while server is running
MODELS_STORE = {"models": [
  {"id":1,"name":"DAMY","country":"Bulgaria","cls":"Class A","gender":"women","from":"2026-01-18","until":"2026-04-13","active":True},
  {"id":2,"name":"SUZANA","country":"Italy","cls":"Class A","gender":"women","from":"2026-01-18","until":"2026-04-13","active":True},
  {"id":3,"name":"LIDIYA","country":"Italy","cls":"Premium Class","gender":"women","from":"2026-01-15","until":"2026-04-14","active":True},
  {"id":4,"name":"DANIELA","country":"France","cls":"Premium Class","gender":"women","from":"2026-01-22","until":"2026-03-09","active":True},
  {"id":5,"name":"THEA","country":"Italy","cls":"Class A","gender":"women","from":"2026-01-11","until":"2026-03-07","active":True},
  {"id":6,"name":"CECILIA","country":"Italy","cls":"Class A","gender":"women","from":"2026-01-11","until":"2026-03-06","active":False},
  {"id":7,"name":"JAMILA","country":"Philippines","cls":"Class A","gender":"women","from":None,"until":None,"active":True},
  {"id":8,"name":"LAURA","country":"Germany","cls":"Class A","gender":"women","from":"2026-03-01","until":"2026-05-01","active":False},
]}

DASHBOARD = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
<title>Fabusse Models — Admin</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@200;300;400;500;700&family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet"/>
<style>
:root{
  --gold:#C9A84C;--gold-l:#E8C97A;--gold-d:#7a5f28;
  --bg:#070709;--dark:#0d0d13;--card:#111118;--card2:#181820;--card3:#1e1e28;
  --border:rgba(201,168,76,.13);--border2:rgba(201,168,76,.06);
  --text:#edeae0;--muted:#6e6e7a;--muted2:#3a3a45;
  --green:#3ecf7a;--red:#e0596a;--blue:#4a8fe0;--orange:#e0a040;--wa:#25D366;
  --radius:10px;--radius-sm:6px;
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent;}
html,body{height:100%;overscroll-behavior:none;}
body{background:var(--bg);color:var(--text);font-family:'Tajawal',sans-serif;font-weight:300;overflow:hidden;}

/* ═══ GLOW BG ═══ */
body::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(ellipse 80% 40% at 60% 0%,rgba(201,168,76,.06),transparent),
             radial-gradient(ellipse 50% 60% at 10% 90%,rgba(201,168,76,.03),transparent);}

/* ═══ LOGIN ═══ */
#login{position:fixed;inset:0;z-index:999;background:var(--bg);display:flex;align-items:center;justify-content:center;padding:24px;}
.login-card{width:100%;max-width:360px;position:relative;z-index:1;}
.login-top{text-align:center;margin-bottom:36px;}
.login-mark{width:64px;height:64px;border:1px solid var(--gold);margin:0 auto 16px;display:flex;align-items:center;justify-content:center;font-family:'Cormorant Garamond',serif;font-size:30px;color:var(--gold);position:relative;}
.login-mark::before{content:'';position:absolute;inset:5px;border:1px solid rgba(201,168,76,.2);}
.login-brand{font-family:'Cormorant Garamond',serif;font-size:28px;letter-spacing:5px;display:block;margin-bottom:4px;}
.login-role{font-size:10px;letter-spacing:3px;color:var(--muted);display:block;}
.lbl{font-size:10px;letter-spacing:2px;color:var(--muted);display:block;margin-bottom:7px;text-transform:uppercase;}
.inp{width:100%;background:var(--card2);border:1px solid rgba(201,168,76,.14);color:var(--text);font-family:'Tajawal',sans-serif;font-size:14px;padding:13px 16px;border-radius:var(--radius-sm);outline:none;transition:border-color .2s;margin-bottom:14px;direction:ltr;text-align:right;}
.inp:focus{border-color:rgba(201,168,76,.4);}
.btn-primary{width:100%;padding:14px;background:var(--gold);color:#000;border:none;cursor:pointer;border-radius:var(--radius-sm);font-family:'Tajawal',sans-serif;font-size:14px;font-weight:500;letter-spacing:1px;transition:all .2s;}
.btn-primary:active{transform:scale(.98);}
.login-err{font-size:12px;color:var(--red);text-align:center;min-height:20px;margin-bottom:8px;}
.login-hint{font-size:11px;color:var(--muted2);text-align:center;margin-top:14px;}

/* ═══ APP SHELL ═══ */
#app{display:none;height:100vh;flex-direction:column;position:relative;z-index:1;}
#app.show{display:flex;}

/* ═══ TOPBAR ═══ */
.topbar{height:56px;background:rgba(7,7,9,.95);backdrop-filter:blur(16px);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 16px;gap:12px;flex-shrink:0;position:relative;z-index:50;}
.topbar-menu{width:36px;height:36px;background:none;border:1px solid var(--border);border-radius:var(--radius-sm);color:var(--muted);font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.topbar-logo{display:flex;align-items:center;gap:8px;flex:1;}
.topbar-mark{width:28px;height:28px;border:1px solid var(--gold);display:flex;align-items:center;justify-content:center;font-family:'Cormorant Garamond',serif;font-size:13px;color:var(--gold);}
.topbar-name{font-family:'Cormorant Garamond',serif;font-size:16px;letter-spacing:2px;}
.topbar-right{display:flex;align-items:center;gap:8px;}
.live-dot-wrap{display:flex;align-items:center;gap:5px;background:rgba(37,211,102,.07);border:1px solid rgba(37,211,102,.2);padding:4px 10px;border-radius:20px;}
.live-dot{width:5px;height:5px;border-radius:50%;background:var(--wa);box-shadow:0 0 6px var(--wa);animation:blink 2s infinite;}
.live-txt{font-size:9px;color:var(--wa);letter-spacing:.5px;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}

/* ═══ BODY ═══ */
.app-body{flex:1;overflow:hidden;display:flex;position:relative;}

/* ═══ SIDEBAR ═══ */
.sidebar{position:absolute;top:0;right:0;bottom:0;width:260px;background:var(--dark);border-left:1px solid var(--border);z-index:100;transform:translateX(260px);transition:transform .3s cubic-bezier(.4,0,.2,1);display:flex;flex-direction:column;}
.sidebar.open{transform:translateX(0);}
.overlay{position:absolute;inset:0;background:rgba(0,0,0,.5);z-index:99;display:none;backdrop-filter:blur(2px);}
.overlay.show{display:block;}

.sb-head{padding:20px 18px 16px;border-bottom:1px solid var(--border);}
.sb-user{display:flex;align-items:center;gap:10px;}
.sb-ava{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,var(--gold-d),rgba(201,168,76,.2));display:flex;align-items:center;justify-content:center;font-size:18px;}
.sb-uname{font-size:13px;font-weight:500;}
.sb-uemail{font-size:10px;color:var(--muted);margin-top:1px;}
.sb-close{background:none;border:none;color:var(--muted);font-size:20px;cursor:pointer;margin-right:auto;}

.sb-nav{flex:1;padding:8px 0;overflow-y:auto;}
.sb-group{font-size:9px;letter-spacing:2px;color:var(--muted2);padding:12px 18px 5px;text-transform:uppercase;}
.sb-link{display:flex;align-items:center;gap:10px;padding:11px 18px;cursor:pointer;color:var(--muted);font-size:13px;transition:all .2s;border-right:2px solid transparent;position:relative;}
.sb-link:hover{color:var(--text);background:rgba(201,168,76,.03);}
.sb-link.active{color:var(--gold);border-right-color:var(--gold);background:rgba(201,168,76,.06);}
.sb-link-icon{font-size:16px;width:22px;text-align:center;}
.sb-link-badge{margin-right:auto;background:var(--gold);color:#000;font-size:9px;font-weight:700;padding:1px 7px;border-radius:10px;}

.sb-foot{padding:14px 18px;border-top:1px solid var(--border);}
.btn-logout{width:100%;padding:10px;background:none;border:1px solid rgba(224,89,106,.25);color:var(--red);cursor:pointer;border-radius:var(--radius-sm);font-family:'Tajawal',sans-serif;font-size:12px;transition:all .2s;letter-spacing:1px;}
.btn-logout:active{background:rgba(224,89,106,.08);}

/* ═══ MAIN CONTENT ═══ */
.main{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;}
.page{display:none;padding:16px;padding-bottom:80px;}
.page.active{display:block;animation:fadeUp .25s ease;}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* ═══ STATS ═══ */
.stats{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;}
.stat{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;position:relative;overflow:hidden;}
.stat::before{content:'';position:absolute;top:-16px;left:-16px;width:60px;height:60px;background:radial-gradient(circle,rgba(201,168,76,.08),transparent);}
.stat-n{font-family:'Cormorant Garamond',serif;font-size:38px;font-weight:300;color:var(--gold);line-height:1;margin-bottom:4px;}
.stat-l{font-size:10px;color:var(--muted);letter-spacing:.5px;}

/* ═══ CARD ═══ */
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;margin-bottom:12px;}
.card-head{padding:13px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;}
.card-title{font-size:10px;letter-spacing:2px;color:var(--gold);font-weight:500;text-transform:uppercase;}
.card-body{padding:16px;}

/* ═══ SECTION DIV ═══ */
.sec{font-size:9px;letter-spacing:3px;color:var(--muted);text-transform:uppercase;display:flex;align-items:center;gap:10px;margin:18px 0 12px;}
.sec::before,.sec::after{content:'';flex:1;height:1px;background:var(--border);}

/* ═══ MODELS ═══ */
.model-card{background:var(--card2);border:1px solid var(--border);border-radius:var(--radius);padding:14px;margin-bottom:10px;display:flex;gap:12px;align-items:flex-start;transition:border-color .2s;position:relative;}
.model-card.off{opacity:.45;}
.model-ava{width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,var(--gold-d),rgba(201,168,76,.15));display:flex;align-items:center;justify-content:center;font-size:22px;border:1px solid var(--border);flex-shrink:0;}
.model-info{flex:1;min-width:0;}
.model-name{font-size:15px;font-weight:500;margin-bottom:2px;}
.model-country{font-size:11px;color:var(--muted);direction:ltr;display:inline-block;margin-bottom:6px;}
.model-cls{display:inline-block;font-size:9px;letter-spacing:1.5px;padding:2px 9px;border-radius:20px;text-transform:uppercase;background:rgba(201,168,76,.1);color:var(--gold);margin-bottom:5px;}
.model-cls.prem{background:rgba(201,168,76,.18);color:var(--gold-l);}
.model-until{font-size:10px;color:var(--muted);direction:ltr;display:block;}
.model-actions-row{display:flex;align-items:center;gap:8px;margin-top:10px;}
.toggle{position:relative;width:44px;height:24px;background:var(--muted2);border:none;border-radius:12px;cursor:pointer;transition:background .3s;flex-shrink:0;}
.toggle.on{background:var(--green);}
.toggle::after{content:'';position:absolute;top:3px;right:3px;width:18px;height:18px;border-radius:50%;background:#fff;transition:transform .3s;box-shadow:0 1px 4px rgba(0,0,0,.3);}
.toggle.on::after{transform:translateX(-20px);}
.toggle-lbl{font-size:11px;color:var(--muted);}
.toggle.on+.toggle-lbl{color:var(--green);}
.icon-btn{background:none;border:1px solid var(--border);color:var(--muted);width:32px;height:32px;border-radius:var(--radius-sm);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:13px;transition:all .2s;margin-right:auto;}
.icon-btn:active{transform:scale(.92);}
.icon-btn.edit:active{border-color:var(--gold);color:var(--gold);}
.icon-btn.del:active{border-color:var(--red);color:var(--red);}

/* ═══ BOOKINGS ═══ */
.bk-card{background:var(--card2);border:1px solid var(--border);border-radius:var(--radius);padding:14px;margin-bottom:10px;cursor:pointer;transition:border-color .2s;}
.bk-card:active{border-color:rgba(201,168,76,.3);}
.bk-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;}
.bk-id{font-family:'Courier New',monospace;font-size:10px;color:var(--gold);direction:ltr;}
.badge{display:inline-block;font-size:9px;letter-spacing:.5px;padding:3px 9px;border-radius:20px;text-transform:uppercase;}
.b-new{background:rgba(201,168,76,.12);color:var(--gold);}
.b-confirmed{background:rgba(62,207,122,.12);color:var(--green);}
.b-pending{background:rgba(74,143,224,.12);color:var(--blue);}
.b-cancelled{background:rgba(224,89,106,.12);color:var(--red);}
.bk-name{font-size:14px;font-weight:500;margin-bottom:3px;}
.bk-meta{font-size:11px;color:var(--muted);display:flex;gap:12px;flex-wrap:wrap;}
.bk-meta span{display:flex;align-items:center;gap:4px;}

/* ═══ FILTER TABS ═══ */
.filter-tabs{display:flex;gap:6px;overflow-x:auto;padding-bottom:4px;margin-bottom:14px;-ms-overflow-style:none;scrollbar-width:none;}
.filter-tabs::-webkit-scrollbar{display:none;}
.ftab{padding:7px 14px;background:var(--card2);border:1px solid var(--border);border-radius:20px;font-size:11px;color:var(--muted);cursor:pointer;white-space:nowrap;transition:all .2s;font-family:'Tajawal',sans-serif;}
.ftab.active{background:rgba(201,168,76,.12);border-color:rgba(201,168,76,.3);color:var(--gold);}

/* ═══ BOTTOM NAV ═══ */
.bottom-nav{position:fixed;bottom:0;left:0;right:0;height:62px;background:rgba(13,13,19,.97);backdrop-filter:blur(16px);border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-around;z-index:50;padding-bottom:env(safe-area-inset-bottom);}
.bnav-item{display:flex;flex-direction:column;align-items:center;gap:3px;padding:6px 12px;cursor:pointer;position:relative;transition:all .2s;}
.bnav-icon{font-size:20px;line-height:1;}
.bnav-lbl{font-size:9px;letter-spacing:.5px;color:var(--muted);}
.bnav-item.active .bnav-lbl{color:var(--gold);}
.bnav-item.active .bnav-icon{filter:drop-shadow(0 0 4px rgba(201,168,76,.5));}
.bnav-badge{position:absolute;top:2px;right:6px;background:var(--gold);color:#000;font-size:8px;font-weight:700;padding:1px 5px;border-radius:10px;min-width:16px;text-align:center;}

/* ═══ MODAL ═══ */
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:200;display:none;align-items:flex-end;justify-content:center;backdrop-filter:blur(4px);}
.modal-bg.open{display:flex;}
.modal{background:var(--card);border-radius:var(--radius) var(--radius) 0 0;width:100%;max-width:560px;max-height:90vh;overflow-y:auto;animation:slideUp .3s cubic-bezier(.34,1.56,.64,1);}
@keyframes slideUp{from{transform:translateY(100%)}to{transform:translateY(0)}}
.modal-head{padding:16px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;background:var(--card);z-index:1;}
.modal-title{font-size:13px;letter-spacing:1.5px;color:var(--gold);}
.modal-close{background:none;border:none;color:var(--muted);font-size:22px;cursor:pointer;line-height:1;padding:4px;}
.modal-body{padding:18px;}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;}
.form-row.full{grid-template-columns:1fr;}
.field{display:flex;flex-direction:column;gap:6px;}
.field label{font-size:9px;letter-spacing:1.5px;color:var(--muted);text-transform:uppercase;}
.field input,.field select,.field textarea{background:var(--card2);border:1px solid rgba(201,168,76,.14);color:var(--text);font-family:'Tajawal',sans-serif;font-size:13px;padding:11px 14px;border-radius:var(--radius-sm);outline:none;transition:border-color .2s;width:100%;}
.field input:focus,.field select:focus,.field textarea:focus{border-color:rgba(201,168,76,.4);}
.field select option{background:var(--dark);}
.modal-foot{padding:14px 18px;border-top:1px solid var(--border);display:flex;gap:10px;}
.btn-cancel{flex:1;padding:12px;background:none;border:1px solid var(--border);color:var(--muted);border-radius:var(--radius-sm);font-family:'Tajawal',sans-serif;font-size:13px;cursor:pointer;}
.btn-save{flex:2;padding:12px;background:var(--gold);color:#000;border:none;border-radius:var(--radius-sm);font-family:'Tajawal',sans-serif;font-size:13px;font-weight:500;cursor:pointer;}
.btn-save:active{transform:scale(.98);}

/* ═══ BOOKING DETAIL MODAL ═══ */
.detail-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border2);}
.detail-row:last-child{border-bottom:none;}
.detail-lbl{font-size:11px;color:var(--muted);}
.detail-val{font-size:12px;color:var(--text);text-align:left;direction:ltr;max-width:60%;}
.status-select{width:100%;background:var(--card2);border:1px solid rgba(201,168,76,.2);color:var(--text);font-family:'Tajawal',sans-serif;font-size:13px;padding:11px 14px;border-radius:var(--radius-sm);outline:none;margin-top:12px;}
.wa-btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;margin-top:10px;padding:12px;background:rgba(37,211,102,.1);border:1px solid rgba(37,211,102,.25);border-radius:var(--radius-sm);color:var(--wa);font-size:13px;text-decoration:none;font-family:'Tajawal',sans-serif;}

/* ═══ CHAT ═══ */
.chat-wrap{height:calc(100vh - 56px - 62px);display:flex;flex-direction:column;background:#0b141a;margin:-16px;margin-bottom:-80px;}
.chat-bar{background:#1f2c34;padding:12px 14px;display:flex;align-items:center;gap:10px;flex-shrink:0;}
.chat-ava{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--gold-d),rgba(201,168,76,.3));display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;}
.chat-info{flex:1;}
.chat-who{font-size:13px;font-weight:500;color:#e9edef;}
.chat-status{font-size:10px;color:#8696a0;margin-top:1px;}
.chat-msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:8px;-webkit-overflow-scrolling:touch;}
.msg{max-width:78%;padding:9px 12px 6px;border-radius:8px;font-size:13px;line-height:1.5;animation:msgIn .25s ease;}
@keyframes msgIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.msg-in{background:#202c33;color:#e9edef;align-self:flex-start;border-radius:0 8px 8px 8px;}
.msg-out{background:#005c4b;color:#e9edef;align-self:flex-end;border-radius:8px 0 8px 8px;}
.msg-time{font-size:10px;color:rgba(255,255,255,.35);margin-top:3px;text-align:left;direction:ltr;}
.msg-out .msg-time{text-align:right;}
.typing-wrap{background:#202c33;padding:10px 14px;border-radius:0 8px 8px 8px;align-self:flex-start;display:none;}
.typing-dots{display:flex;gap:4px;}
.typing-dots span{width:7px;height:7px;border-radius:50%;background:#8696a0;animation:dot 1.4s infinite;}
.typing-dots span:nth-child(2){animation-delay:.2s;}
.typing-dots span:nth-child(3){animation-delay:.4s;}
@keyframes dot{0%,60%,100%{transform:scale(1);opacity:.5}30%{transform:scale(1.3);opacity:1}}
.quick-wrap{padding:8px 12px;background:#0b141a;border-top:1px solid rgba(255,255,255,.05);display:flex;gap:6px;overflow-x:auto;flex-shrink:0;}
.quick-wrap::-webkit-scrollbar{display:none;}
.qbtn{background:rgba(37,211,102,.08);border:1px solid rgba(37,211,102,.2);color:var(--wa);padding:7px 12px;border-radius:16px;font-size:11px;cursor:pointer;white-space:nowrap;font-family:'Tajawal',sans-serif;}
.chat-input-row{background:#1f2c34;padding:10px 12px;display:flex;gap:8px;align-items:center;flex-shrink:0;}
.chat-inp{flex:1;background:#2a3942;border:none;border-radius:20px;padding:10px 16px;color:#e9edef;font-family:'Tajawal',sans-serif;font-size:13px;outline:none;direction:rtl;}
.chat-inp::placeholder{color:#8696a0;}
.chat-send{width:40px;height:40px;border-radius:50%;background:var(--wa);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;color:#fff;}
.chat-send:active{transform:scale(.92);}

/* ═══ SETTINGS ═══ */
.setting-item{display:flex;align-items:center;justify-content:space-between;padding:14px 0;border-bottom:1px solid var(--border2);}
.setting-item:last-child{border-bottom:none;}
.setting-info{}
.setting-lbl{font-size:13px;font-weight:400;margin-bottom:3px;}
.setting-desc{font-size:11px;color:var(--muted);}

/* ═══ SEARCH ═══ */
.search{display:flex;align-items:center;gap:8px;background:var(--card2);border:1px solid var(--border);border-radius:var(--radius-sm);padding:10px 14px;margin-bottom:14px;}
.search input{background:none;border:none;color:var(--text);font-family:'Tajawal',sans-serif;font-size:13px;outline:none;flex:1;direction:rtl;}
.search input::placeholder{color:var(--muted);}

/* ═══ TOAST ═══ */
.toast{position:fixed;bottom:72px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--card);border:1px solid var(--gold);border-radius:var(--radius-sm);padding:10px 20px;font-size:12px;display:flex;align-items:center;gap:8px;opacity:0;transition:all .3s cubic-bezier(.34,1.56,.64,1);z-index:999;white-space:nowrap;pointer-events:none;}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0);}

/* ═══ EMPTY ═══ */
.empty{text-align:center;padding:48px 24px;color:var(--muted);}
.empty-icon{font-size:42px;display:block;margin-bottom:12px;opacity:.3;}

/* ═══ ADD FAB ═══ */
.fab{position:fixed;bottom:76px;left:20px;width:48px;height:48px;background:var(--gold);border:none;border-radius:50%;font-size:22px;color:#000;cursor:pointer;z-index:51;box-shadow:0 4px 20px rgba(201,168,76,.35);display:none;align-items:center;justify-content:center;transition:transform .2s;}
.fab.show{display:flex;}
.fab:active{transform:scale(.92);}

/* scrollbar */
*::-webkit-scrollbar{width:3px;height:3px;}
*::-webkit-scrollbar-thumb{background:rgba(201,168,76,.15);border-radius:2px;}
</style>
</head>
<body>

<!-- ══════════ LOGIN ══════════ -->
<div id="login">
  <div class="login-card">
    <div class="login-top">
      <div class="login-mark">F</div>
      <span class="login-brand">FABUSSE</span>
      <span class="login-role">Admin Dashboard · Kuwait</span>
    </div>
    <label class="lbl">اسم المستخدم</label>
    <input class="inp" id="lu" type="text" placeholder="admin" autocomplete="username"/>
    <label class="lbl">كلمة المرور</label>
    <input class="inp" id="lp" type="password" placeholder="••••••••" onkeypress="if(event.key==='Enter')doLogin()"/>
    <div class="login-err" id="lerr"></div>
    <button class="btn-primary" onclick="doLogin()">دخول</button>
    <div class="login-hint">تجريبي: admin / fabusse2024</div>
  </div>
</div>

<!-- ══════════ APP ══════════ -->
<div id="app">

  <!-- TOPBAR -->
  <div class="topbar">
    <button class="topbar-menu" onclick="openSidebar()">☰</button>
    <div class="topbar-logo">
      <div class="topbar-mark">F</div>
      <div class="topbar-name">FABUSSE</div>
    </div>
    <div class="topbar-right">
      <div class="live-dot-wrap">
        <div class="live-dot"></div>
        <div class="live-txt">متصل</div>
      </div>
    </div>
  </div>

  <!-- BODY -->
  <div class="app-body">

    <!-- SIDEBAR -->
    <div class="overlay" id="overlay" onclick="closeSidebar()"></div>
    <div class="sidebar" id="sidebar">
      <div class="sb-head">
        <div class="sb-user">
          <div class="sb-ava">👤</div>
          <div>
            <div class="sb-uname">Ramez Basmaji</div>
            <div class="sb-uemail"><a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="a9c0c7cfc6e9cfc8cbdcdadaccc4c6cdccc5da87cac6c4">[email&#160;protected]</a></div>
          </div>
          <button class="sb-close" onclick="closeSidebar()">✕</button>
        </div>
      </div>
      <nav class="sb-nav">
        <div class="sb-group">الرئيسية</div>
        <div class="sb-link active" onclick="goPage('dashboard',this)"><span class="sb-link-icon">📊</span>لوحة التحكم</div>
        <div class="sb-group">إدارة</div>
        <div class="sb-link" onclick="goPage('models',this)"><span class="sb-link-icon">👑</span>الموديلز</div>
        <div class="sb-link" onclick="goPage('bookings',this)"><span class="sb-link-icon">📋</span>الحجوزات<span class="sb-link-badge" id="sb-badge">0</span></div>
        <div class="sb-link" onclick="goPage('chat',this)"><span class="sb-link-icon">💬</span>تجربة الشات</div>
        <div class="sb-group">النظام</div>
        <div class="sb-link" onclick="goPage('settings',this)"><span class="sb-link-icon">⚙️</span>الإعدادات</div>
      </nav>
      <div class="sb-foot">
        <button class="btn-logout" onclick="doLogout()">🚪 تسجيل الخروج</button>
      </div>
    </div>

    <!-- MAIN -->
    <div class="main" id="main">

      <!-- DASHBOARD -->
      <div id="page-dashboard" class="page active">
        <div class="stats">
          <div class="stat"><div class="stat-n" id="ds-total">3</div><div class="stat-l">إجمالي الحجوزات</div></div>
          <div class="stat"><div class="stat-n" id="ds-active">7</div><div class="stat-l">موديلز متاحين</div></div>
          <div class="stat"><div class="stat-n" id="ds-new">1</div><div class="stat-l">حجوزات جديدة</div></div>
          <div class="stat"><div class="stat-n" id="ds-confirmed">1</div><div class="stat-l">مؤكدة</div></div>
        </div>
        <div class="sec">آخر الحجوزات</div>
        <div id="dash-bks"></div>
        <div class="sec">حالة النظام</div>
        <div class="card">
          <div class="card-body">
            <div class="setting-item">
              <div class="setting-info"><div class="setting-lbl">WhatsApp Agent</div><div class="setting-desc">يستقبل الرسائل ويرد</div></div>
              <span class="badge b-confirmed">فعّال</span>
            </div>
            <div class="setting-item">
              <div class="setting-info"><div class="setting-lbl">Claude AI</div><div class="setting-desc">يفهم ويحلل الطلبات</div></div>
              <span class="badge b-confirmed">متصل</span>
            </div>
            <div class="setting-item">
              <div class="setting-info"><div class="setting-lbl">إيميل الإشعارات</div><div class="setting-desc"><a href="/cdn-cgi/l/email-protection" class="__cf_email__" data-cfemail="40292e262f00262122353333252d2f24252c336e232f2d">[email&#160;protected]</a></div></div>
              <span class="badge b-confirmed">جاهز</span>
            </div>
          </div>
        </div>
      </div>

      <!-- MODELS -->
      <div id="page-models" class="page">
        <div class="search"><span>🔍</span><input type="text" placeholder="ابحث عن موديل..." oninput="filterModels(this.value)"/></div>
        <div id="models-list"></div>
      </div>

      <!-- BOOKINGS -->
      <div id="page-bookings" class="page">
        <div class="filter-tabs" id="ftabs">
          <div class="ftab active" onclick="setFilter('all',this)">الكل</div>
          <div class="ftab" onclick="setFilter('new',this)">🆕 جديد</div>
          <div class="ftab" onclick="setFilter('confirmed',this)">✅ مؤكد</div>
          <div class="ftab" onclick="setFilter('pending',this)">⏳ قيد المعالجة</div>
          <div class="ftab" onclick="setFilter('cancelled',this)">❌ ملغي</div>
        </div>
        <div id="bk-list"></div>
      </div>

      <!-- CHAT -->
      <div id="page-chat" class="page" style="padding:0;padding-bottom:0;">
        <div class="chat-wrap">
          <div class="chat-bar">
            <div class="chat-ava">🤖</div>
            <div class="chat-info">
              <div class="chat-who">Fabusse Agent</div>
              <div class="chat-status">جرّب كأنك زبون</div>
            </div>
          </div>
          <div class="chat-msgs" id="chat-msgs">
            <div class="msg msg-in">أهلاً! 👋 أنا المساعد الذكي لوكالة <strong>Fabusse Models</strong> في الكويت.<br>كيف أقدر أساعدك؟ 😊<div class="msg-time">الآن</div></div>
          </div>
          <div class="typing-wrap" id="typing"><div class="typing-dots"><span></span><span></span><span></span></div></div>
          <div class="quick-wrap">
            <button class="qbtn" onclick="sendQ('أبي أحجز موديل')">📸 حجز موديل</button>
            <button class="qbtn" onclick="sendQ('كم أسعاركم؟')">💰 الأسعار</button>
            <button class="qbtn" onclick="sendQ('وين موقعكم؟')">📍 الموقع</button>
            <button class="qbtn" onclick="sendQ('عندكم موديلز إيطاليين؟')">🌍 الموديلز</button>
            <button class="qbtn" onclick="sendQ('عندكم استوديو؟')">🎬 الاستوديو</button>
          </div>
          <div class="chat-input-row">
            <button class="chat-send" onclick="sendMsg()">➤</button>
            <input class="chat-inp" id="chat-inp" placeholder="اكتب رسالتك..." onkeypress="if(event.key==='Enter')sendMsg()"/>
          </div>
        </div>
      </div>

      <!-- SETTINGS -->
      <div id="page-settings" class="page">
        <div class="card" style="margin-bottom:12px;">
          <div class="card-head"><div class="card-title">WhatsApp API</div></div>
          <div class="card-body">
            <div class="field" style="margin-bottom:10px;"><label>Phone Number ID</label><input type="text" placeholder="123456789012345" style="direction:ltr;"/></div>
            <div class="field" style="margin-bottom:10px;"><label>Access Token</label><input type="password" placeholder="EAAG..."/></div>
            <div class="field" style="margin-bottom:14px;"><label>Verify Token</label><input type="text" placeholder="fabusse2024" style="direction:ltr;"/></div>
            <button class="btn-save" style="width:100%;padding:12px;border-radius:6px;" onclick="toast('تم حفظ إعدادات واتساب ✓')">حفظ</button>
          </div>
        </div>
        <div class="card" style="margin-bottom:12px;">
          <div class="card-head"><div class="card-title">Claude AI API</div></div>
          <div class="card-body">
            <div class="field" style="margin-bottom:10px;">
              <label>API Key</label>
              <input type="password" id="claude-api-key" placeholder="sk-ant-api03-..." style="direction:ltr;"/>
            </div>
            <div class="field" style="margin-bottom:6px;"><label>الموديل</label><select><option>claude-sonnet-4-6</option><option>claude-opus-4-6</option></select></div>
            <div style="font-size:10px;color:var(--muted);margin-bottom:14px;line-height:1.5;">الـ Key يُحفظ في المتصفح فقط — لا يُرسل لأي خادم</div>
            <button class="btn-save" style="width:100%;padding:12px;border-radius:6px;" onclick="saveApiKey()">حفظ الـ API Key</button>
          </div>
        </div>
        <div class="card">
          <div class="card-head"><div class="card-title">إيميل الإشعارات</div></div>
          <div class="card-body">
            <div class="field" style="margin-bottom:10px;"><label>إيميل صاحب البيزنس</label><input type="email" value="info@fabussemodels.com" style="direction:ltr;"/></div>
            <div class="field" style="margin-bottom:14px;"><label>Gmail App Password</label><input type="password" placeholder="xxxx xxxx xxxx xxxx"/></div>
            <button class="btn-save" style="width:100%;padding:12px;border-radius:6px;" onclick="toast('تم حفظ إعدادات الإيميل ✓')">حفظ</button>
          </div>
        </div>
      </div>

    </div><!-- /main -->
  </div><!-- /app-body -->

  <!-- BOTTOM NAV -->
  <div class="bottom-nav">
    <div class="bnav-item active" id="bn-dashboard" onclick="goPage('dashboard')">
      <div class="bnav-icon">📊</div>
      <div class="bnav-lbl">الرئيسية</div>
    </div>
    <div class="bnav-item" id="bn-models" onclick="goPage('models')">
      <div class="bnav-icon">👑</div>
      <div class="bnav-lbl">الموديلز</div>
    </div>
    <div class="bnav-item" id="bn-bookings" onclick="goPage('bookings')">
      <div class="bnav-icon">📋</div>
      <div class="bnav-lbl">الحجوزات</div>
      <div class="bnav-badge" id="bk-badge">1</div>
    </div>
    <div class="bnav-item" id="bn-chat" onclick="goPage('chat')">
      <div class="bnav-icon">💬</div>
      <div class="bnav-lbl">الشات</div>
    </div>
    <div class="bnav-item" id="bn-settings" onclick="goPage('settings')">
      <div class="bnav-icon">⚙️</div>
      <div class="bnav-lbl">الإعدادات</div>
    </div>
  </div>

  <!-- FAB -->
  <button class="fab" id="fab" onclick="openAddModel()">＋</button>

</div><!-- /app -->

<!-- ══════ MODEL MODAL ══════ -->
<div class="modal-bg" id="model-modal">
  <div class="modal">
    <div class="modal-head">
      <div class="modal-title" id="modal-title">إضافة موديل</div>
      <button class="modal-close" onclick="closeModal('model-modal')">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-row">
        <div class="field"><label>الاسم</label><input id="m-name" placeholder="SOPHIA"/></div>
        <div class="field"><label>البلد</label><input id="m-country" placeholder="Italy"/></div>
      </div>
      <div class="form-row">
        <div class="field"><label>الفئة</label>
          <select id="m-cls"><option>Premium Class</option><option>Class A</option><option>Local Model</option><option>Kids Model</option></select>
        </div>
        <div class="field"><label>الجنس</label>
          <select id="m-gender"><option value="women">نساء</option><option value="men">رجال</option><option value="kids">أطفال</option></select>
        </div>
      </div>
      <div class="form-row">
        <div class="field"><label>تاريخ الوصول</label><input id="m-from" type="date" style="direction:ltr;"/></div>
        <div class="field"><label>تاريخ المغادرة</label><input id="m-until" type="date" style="direction:ltr;"/></div>
      </div>
    </div>
    <div class="modal-foot">
      <button class="btn-cancel" onclick="closeModal('model-modal')">إلغاء</button>
      <button class="btn-save" onclick="saveModel()">حفظ الموديل</button>
    </div>
  </div>
</div>

<!-- ══════ BOOKING DETAIL MODAL ══════ -->
<div class="modal-bg" id="bk-modal">
  <div class="modal">
    <div class="modal-head">
      <div class="modal-title" id="bk-modal-id">تفاصيل الحجز</div>
      <button class="modal-close" onclick="closeModal('bk-modal')">✕</button>
    </div>
    <div class="modal-body" id="bk-modal-body"></div>
  </div>
</div>

<!-- TOAST -->
<div class="toast" id="toast-el">✓ <span id="toast-txt"></span></div>

<script data-cfasync="false" src="/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js"></script><script>
// ══════════════════════
// DATA
// ══════════════════════
let MODELS = [
  {id:1,name:'DAMY',country:'Bulgaria',cls:'Class A',gender:'women',from:'2026-01-18',until:'2026-04-13',active:true},
  {id:2,name:'SUZANA',country:'Italy',cls:'Class A',gender:'women',from:'2026-01-18',until:'2026-04-13',active:true},
  {id:3,name:'LIDIYA',country:'Italy',cls:'Premium Class',gender:'women',from:'2026-01-15',until:'2026-04-14',active:true},
  {id:4,name:'DANIELA',country:'France',cls:'Premium Class',gender:'women',from:'2026-01-22',until:'2026-03-09',active:true},
  {id:5,name:'THEA',country:'Italy',cls:'Class A',gender:'women',from:'2026-01-11',until:'2026-03-07',active:true},
  {id:6,name:'CECILIA',country:'Italy',cls:'Class A',gender:'women',from:'2026-01-11',until:'2026-03-06',active:false},
  {id:7,name:'JAMILA',country:'Philippines',cls:'Class A',gender:'women',from:null,until:null,active:true},
  {id:8,name:'LAURA',country:'Germany',cls:'Class A',gender:'women',from:'2026-03-01',until:'2026-05-01',active:false},
];

let BOOKINGS = [
  {id:'FBM-20260304-A1B2',name:'محمد العنزي',phone:'96550123456',service:'فاشن شو',model:'Premium Class',date:'2026-03-15',time:'10:00',location:'360 Mall',duration:'يوم كامل',budget:'—',notes:'محتاج موديلين أوروبيين',status:'new',received:'04/03/2026 09:22'},
  {id:'FBM-20260303-C3D4',name:'سارة الرشيدي',phone:'96559876543',service:'تصوير كتالوج',model:'Class A',date:'2026-03-20',time:'14:00',location:'The Gate',duration:'نصف يوم',budget:'500 KWD',notes:'كتالوج ربيع 2026',status:'confirmed',received:'03/03/2026 15:40'},
  {id:'FBM-20260302-E5F6',name:'فيصل المطيري',phone:'96565432109',service:'حملة سوشيال',model:'Local Model',date:'2026-03-10',time:'11:00',location:'سالمية',duration:'4 ساعات',budget:'—',notes:'حملة إنستقرام لمطعم',status:'pending',received:'02/03/2026 11:15'},
];

let editModelId = null;
let bkFilter = 'all';
let curPage = 'dashboard';
let nextId = 9;
// Claude API chat — no staged flow needed

// ══════════════════════
// LOGIN
// ══════════════════════
function doLogin(){
  const u=document.getElementById('lu').value.trim();
  const p=document.getElementById('lp').value.trim();
  if(u==='admin'&&p==='fabusse2024'){
    const l=document.getElementById('login');
    l.style.transition='opacity .35s';l.style.opacity='0';
    setTimeout(()=>{l.style.display='none';document.getElementById('app').classList.add('show');renderAll();},350);
  } else {
    document.getElementById('lerr').textContent='بيانات الدخول غير صحيحة';
    document.getElementById('lp').value='';
  }
}
function doLogout(){
  document.getElementById('app').classList.remove('show');
  const l=document.getElementById('login');
  l.style.display='flex';l.style.opacity='1';
  document.getElementById('lp').value='';
  document.getElementById('lerr').textContent='';
}

// ══════════════════════
// NAVIGATION
// ══════════════════════
function goPage(p, sbEl){
  curPage=p;
  document.querySelectorAll('.page').forEach(x=>x.classList.remove('active'));
  document.getElementById('page-'+p).classList.add('active');
  document.querySelectorAll('.bnav-item').forEach(x=>x.classList.remove('active'));
  const bn=document.getElementById('bn-'+p);
  if(bn) bn.classList.add('active');
  document.querySelectorAll('.sb-link').forEach(x=>x.classList.remove('active'));
  if(sbEl) sbEl.classList.add('active');
  const fab=document.getElementById('fab');
  fab.classList.toggle('show', p==='models');
  closeSidebar();
  if(p==='models') renderModels();
  if(p==='bookings') renderBookings();
  if(p==='dashboard') renderDash();
}

function openSidebar(){document.getElementById('sidebar').classList.add('open');document.getElementById('overlay').classList.add('show');}
function closeSidebar(){document.getElementById('sidebar').classList.remove('open');document.getElementById('overlay').classList.remove('show');}

// ══════════════════════
// RENDER ALL
// ══════════════════════
function renderAll(){
  // fetch models from server first
  fetch('/models').then(r=>r.json()).then(data=>{
    if(data.models) MODELS = data.models;
    renderDash();renderModels();renderBookings();updateBadge();loadApiKey();
  }).catch(()=>{
    renderDash();renderModels();renderBookings();updateBadge();loadApiKey();
  });
}
function saveApiKey(){
  const k=document.getElementById('claude-api-key').value.trim();
  if(k) localStorage.setItem('fbm_key',k);
  toast('✓ تم حفظ الـ Key — الشات جاهز!');
}
function loadApiKey(){
  const k=localStorage.getItem('fbm_key');
  const el=document.getElementById('claude-api-key');
  if(k&&el) el.value=k;
}

// ══════════════════════
// DASHBOARD
// ══════════════════════
function renderDash(){
  const active=MODELS.filter(m=>m.active).length;
  const newBk=BOOKINGS.filter(b=>b.status==='new').length;
  const conf=BOOKINGS.filter(b=>b.status==='confirmed').length;
  document.getElementById('ds-total').textContent=BOOKINGS.length;
  document.getElementById('ds-active').textContent=active;
  document.getElementById('ds-new').textContent=newBk;
  document.getElementById('ds-confirmed').textContent=conf;
  const c=document.getElementById('dash-bks');
  if(!BOOKINGS.length){c.innerHTML='<div class="empty"><span class="empty-icon">📭</span>لا توجد حجوزات</div>';return;}
  c.innerHTML=BOOKINGS.slice(0,3).map(b=>`
    <div class="bk-card" onclick="openBkDetail('${b.id}')">
      <div class="bk-top"><span class="bk-id">${b.id}</span><span class="badge ${bClass(b.status)}">${bLabel(b.status)}</span></div>
      <div class="bk-name">${b.name}</div>
      <div class="bk-meta"><span>📸 ${b.service}</span><span>📅 ${b.date}</span></div>
    </div>`).join('');
}

// ══════════════════════
// MODELS
// ══════════════════════
function renderModels(q=''){
  const list=q?MODELS.filter(m=>m.name.toLowerCase().includes(q.toLowerCase())||m.country.toLowerCase().includes(q.toLowerCase())):MODELS;
  const c=document.getElementById('models-list');
  if(!list.length){c.innerHTML='<div class="empty"><span class="empty-icon">👤</span>لا يوجد موديلز</div>';return;}
  c.innerHTML=list.map(m=>`
    <div class="model-card ${m.active?'':'off'}" id="mc-${m.id}">
      <div class="model-ava">${m.gender==='men'?'👨':'👩'}</div>
      <div class="model-info">
        <div class="model-name">${m.name}</div>
        <div class="model-country">🌍 ${m.country}</div>
        <span class="model-cls ${m.cls==='Premium Class'?'prem':''}">${m.cls}</span>
        <div class="model-until">${m.until?'حتى '+fmtDate(m.until):'محلية · دائمة'}</div>
        <div class="model-actions-row">
          <button class="toggle ${m.active?'on':''}" onclick="toggleM(${m.id})"></button>
          <span class="toggle-lbl">${m.active?'متاحة':'غير متاحة'}</span>
          <button class="icon-btn edit" onclick="openEditModel(${m.id})">✏️</button>
          <button class="icon-btn del" onclick="delModel(${m.id})">🗑</button>
        </div>
      </div>
    </div>`).join('');
}
function filterModels(v){renderModels(v);}

function toggleM(id){
  const m=MODELS.find(x=>x.id===id);if(!m)return;
  m.active=!m.active;
  renderModels();renderDash();updateBadge();syncModels();
  toast(`${m.name} — ${m.active?'تم التفعيل ✓':'تم التعطيل'}`);
}
function delModel(id){
  const m=MODELS.find(x=>x.id===id);if(!m)return;
  if(!confirm(`حذف ${m.name}؟`))return;
  MODELS=MODELS.filter(x=>x.id!==id);
  renderModels();renderDash();syncModels();
  toast(`تم حذف ${m.name}`);
}
function openAddModel(){
  editModelId=null;
  document.getElementById('modal-title').textContent='إضافة موديل جديد';
  ['m-name','m-country'].forEach(i=>document.getElementById(i).value='');
  document.getElementById('m-from').value='';document.getElementById('m-until').value='';
  openModal('model-modal');
}
function openEditModel(id){
  const m=MODELS.find(x=>x.id===id);if(!m)return;
  editModelId=id;
  document.getElementById('modal-title').textContent='تعديل '+m.name;
  document.getElementById('m-name').value=m.name;
  document.getElementById('m-country').value=m.country;
  document.getElementById('m-cls').value=m.cls;
  document.getElementById('m-gender').value=m.gender;
  document.getElementById('m-from').value=m.from||'';
  document.getElementById('m-until').value=m.until||'';
  openModal('model-modal');
}
function saveModel(){
  const name=document.getElementById('m-name').value.trim();
  const country=document.getElementById('m-country').value.trim();
  if(!name||!country){toast('الاسم والبلد مطلوبان');return;}
  if(editModelId){
    const m=MODELS.find(x=>x.id===editModelId);
    m.name=name;m.country=country;m.cls=document.getElementById('m-cls').value;
    m.gender=document.getElementById('m-gender').value;
    m.from=document.getElementById('m-from').value||null;
    m.until=document.getElementById('m-until').value||null;
    toast(`تم تحديث ${name} ✓`);
  } else {
    MODELS.push({id:nextId++,name,country,cls:document.getElementById('m-cls').value,gender:document.getElementById('m-gender').value,from:document.getElementById('m-from').value||null,until:document.getElementById('m-until').value||null,active:true});
    toast(`تمت إضافة ${name} ✓`);
  }
  closeModal('model-modal');renderModels();renderDash();syncModels();
}

// ══════════════════════
// BOOKINGS
// ══════════════════════
function setFilter(f,el){
  bkFilter=f;
  document.querySelectorAll('.ftab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  renderBookings();
}
function renderBookings(){
  const list=bkFilter==='all'?BOOKINGS:BOOKINGS.filter(b=>b.status===bkFilter);
  const c=document.getElementById('bk-list');
  if(!list.length){c.innerHTML='<div class="empty"><span class="empty-icon">📋</span>لا توجد حجوزات</div>';return;}
  c.innerHTML=list.map(b=>`
    <div class="bk-card" onclick="openBkDetail('${b.id}')">
      <div class="bk-top"><span class="bk-id">${b.id}</span><span class="badge ${bClass(b.status)}">${bLabel(b.status)}</span></div>
      <div class="bk-name">${b.name}</div>
      <div class="bk-meta">
        <span>📸 ${b.service}</span>
        <span>👑 ${b.model}</span>
        <span>📅 ${b.date}</span>
        <span>📍 ${b.location}</span>
      </div>
    </div>`).join('');
}
function openBkDetail(id){
  const b=BOOKINGS.find(x=>x.id===id);if(!b)return;
  document.getElementById('bk-modal-id').textContent=b.id;
  document.getElementById('bk-modal-body').innerHTML=`
    <div class="detail-row"><span class="detail-lbl">العميل</span><span class="detail-val">${b.name}</span></div>
    <div class="detail-row"><span class="detail-lbl">الجوال</span><span class="detail-val">${b.phone}</span></div>
    <div class="detail-row"><span class="detail-lbl">الخدمة</span><span class="detail-val">${b.service}</span></div>
    <div class="detail-row"><span class="detail-lbl">فئة الموديل</span><span class="detail-val">${b.model}</span></div>
    <div class="detail-row"><span class="detail-lbl">التاريخ</span><span class="detail-val">${b.date} — ${b.time}</span></div>
    <div class="detail-row"><span class="detail-lbl">الموقع</span><span class="detail-val">${b.location}</span></div>
    <div class="detail-row"><span class="detail-lbl">المدة</span><span class="detail-val">${b.duration}</span></div>
    <div class="detail-row"><span class="detail-lbl">الميزانية</span><span class="detail-val">${b.budget}</span></div>
    <div class="detail-row"><span class="detail-lbl">الملاحظات</span><span class="detail-val">${b.notes}</span></div>
    <div class="detail-row"><span class="detail-lbl">وقت الاستلام</span><span class="detail-val">${b.received}</span></div>
    <div style="margin-top:14px;">
      <div style="font-size:10px;letter-spacing:1.5px;color:var(--muted);margin-bottom:7px;text-transform:uppercase;">تغيير الحالة</div>
      <select class="status-select" onchange="changeStatus('${b.id}',this.value)">
        <option value="new" ${b.status==='new'?'selected':''}>🆕 جديد</option>
        <option value="confirmed" ${b.status==='confirmed'?'selected':''}>✅ مؤكد</option>
        <option value="pending" ${b.status==='pending'?'selected':''}>⏳ قيد المعالجة</option>
        <option value="cancelled" ${b.status==='cancelled'?'selected':''}>❌ ملغي</option>
      </select>
    </div>
    <a class="wa-btn" href="https://wa.me/${b.phone}" target="_blank">💬 رد على واتساب الزبون</a>`;
  openModal('bk-modal');
}
function changeStatus(id,s){
  const b=BOOKINGS.find(x=>x.id===id);if(b){b.status=s;}
  renderBookings();renderDash();updateBadge();
  toast('تم تحديث الحالة ✓');
}

// ══════════════════════
// CHAT — Claude API
// ══════════════════════
let chatHistory = [];

function getApiKey(){
  const el = document.getElementById('claude-api-key');
  if(el && el.value.trim()) return el.value.trim();
  return localStorage.getItem('fbm_key')||'';
}

function buildSystemPrompt(){
  const activeList = MODELS.filter(m=>m.active)
    .map(m=>`- ${m.name} (${m.country}) — ${m.cls}${m.until?' — available until '+fmtDate(m.until):''}`)
    .join('\\n');
  return `You are the official WhatsApp booking assistant for Fabusse Models Agency in Kuwait.
You have a warm, natural, conversational personality — like a helpful friend who works at a luxury agency. Never sound robotic or scripted.
Always reply in the SAME language the user writes in (Arabic or English). If they mix, follow their lead.
Use natural emojis occasionally but don't overdo it.

ABOUT FABUSSE MODELS:
- Kuwait's premier international modeling agency
- Owner: Ramez Basmaji | License: 2023/16035
- Location: Salmiya, Block 9, Salem Al Mubarak St, Northern Tower, Floor 7, Office 701
- Phone: +965 99198990 / +965 98747673
- Email: info@fabussemodels.com | Instagram: @fabussemodels
- Services: Runway/Fashion Shows, Catalogue & E-Commerce Shoots, Brand Ambassador, Event Hostess, Social Media Campaigns, Lookbook, Commercial Filming, Kids Campaigns
- Also has a professional photography Studio and a Modeling School

MODELS CURRENTLY IN KUWAIT (ACTIVE ONLY):
${activeList || '- No models currently active'}

PRICING: Never give specific prices. Say pricing depends on model category, duration, and service type — offer to prepare a custom quote once you have their details.

BOOKING: Naturally collect these details in conversation (don't make it feel like a form):
service type → model category → event date & time → location → duration → budget (optional) → email (optional)

When you have enough info (at least: service, model category, date, location), say booking is received and include this exact JSON on a new line so the system can process it:
BOOKING_DATA:{"service_type":"...","model_category":"...","event_date":"...","event_time":"...","location":"...","duration":"...","budget":"...","email":"..."}

IMPORTANT RULES:
- Be natural and conversational, never copy-paste feeling
- If asked about unavailable models, apologize and suggest available ones
- If asked something unrelated to the agency, politely bring conversation back
- Keep responses concise — this is WhatsApp, not email`;
}

function getTime(){return new Date().toLocaleTimeString('ar',{hour:'2-digit',minute:'2-digit'});}

function addMsg(txt, out){
  const c = document.getElementById('chat-msgs');
  const d = document.createElement('div');
  d.className = 'msg '+(out?'msg-out':'msg-in');
  // clean booking data line from display
  const display = txt.replace(/BOOKING_DATA:\\{.*?\\}/g,'').trim();
  d.innerHTML = display.replace(/\\n/g,'<br>').replace(/\\*(.*?)\\*/g,'<strong>$1</strong>') + `<div class="msg-time">${getTime()}</div>`;
  c.appendChild(d);
  c.scrollTop = c.scrollHeight;
}

function checkBookingData(txt){
  const match = txt.match(/BOOKING_DATA:(\\{.*?\\})/);
  if(!match) return;
  try {
    const data = JSON.parse(match[1]);
    const id = genId();
    const bk = {
      id, name:'زبون واتساب', phone:'96500000000',
      service: data.service_type||'N/A',
      model: data.model_category||'N/A',
      date: data.event_date||'N/A',
      time: data.event_time||'N/A',
      location: data.location||'N/A',
      duration: data.duration||'N/A',
      budget: data.budget||'—',
      notes: 'حجز من الشات التجريبي',
      status:'new',
      received: new Date().toLocaleString('ar-KW')
    };
    BOOKINGS.unshift(bk);
    renderDash(); renderBookings(); updateBadge();
    toast('📋 حجز جديد أضيف تلقائياً! '+id);
  } catch(e){}
}

async function sendMsg(){
  const inp = document.getElementById('chat-inp');
  const msg = inp.value.trim();
  if(!msg) return;
  inp.value = '';
  inp.disabled = true;

  addMsg(msg, true);
  chatHistory.push({role:'user', content: msg});

  const typ = document.getElementById('typing');
  typ.style.display = 'block';
  document.getElementById('chat-msgs').scrollTop = 99999;

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        system: buildSystemPrompt(),
        messages: chatHistory
      })
    });

    const data = await res.json();
    typ.style.display='none';
    inp.disabled=false; inp.focus();

    if(data.error){
      addMsg('❌ ' + (data.error.message||JSON.stringify(data.error)), false);
      return;
    }

    const reply = data.content.map(b=>b.text||'').join('');
    chatHistory.push({role:'assistant', content: reply});
    addMsg(reply, false);
    checkBookingData(reply);

  } catch(e){
    typ.style.display='none';
    inp.disabled=false;
    addMsg('❌ خطأ: ' + e.message, false);
  }
}

function sendQ(msg){document.getElementById('chat-inp').value=msg;sendMsg();}

// ══════════════════════
// HELPERS
// ══════════════════════

function syncModels(){
  fetch('/models',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({models:MODELS})})
  .catch(e=>console.log('sync error',e));
}
function genId(){
  const n=new Date();
  return`FBM-${n.getFullYear()}${String(n.getMonth()+1).padStart(2,'0')}${String(n.getDate()).padStart(2,'0')}-${Math.random().toString(36).toUpperCase().replace(/[^A-Z0-9]/g,'').slice(0,4).padEnd(4,'0')}`;
}
function fmtDate(d){if(!d)return'';const p=d.split('-');return`${p[2]}/${p[1]}/${p[0]}`;}
function bClass(s){return{new:'b-new',confirmed:'b-confirmed',pending:'b-pending',cancelled:'b-cancelled'}[s]||'b-new';}
function bLabel(s){return{new:'جديد',confirmed:'مؤكد',pending:'قيد المعالجة',cancelled:'ملغي'}[s]||s;}
function updateBadge(){
  const n=BOOKINGS.filter(b=>b.status==='new').length;
  document.getElementById('bk-badge').textContent=n;
  document.getElementById('sb-badge').textContent=n;
  document.getElementById('bk-badge').style.display=n?'block':'none';
}
function openModal(id){document.getElementById(id).classList.add('open');}
function closeModal(id){document.getElementById(id).classList.remove('open');}
function toast(msg){
  const t=document.getElementById('toast-el');
  document.getElementById('toast-txt').textContent=msg;
  t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2500);
}
// close modal on bg click
document.querySelectorAll('.modal-bg').forEach(m=>{
  m.addEventListener('click',function(e){if(e.target===this)this.classList.remove('open');});
});
</script>
</body>
</html>'''

@app.route("/", methods=["GET"])
def home():
    return Response(DASHBOARD, mimetype="text/html")

@app.route("/models", methods=["GET"])
def get_models():
    return jsonify(MODELS_STORE)

@app.route("/models", methods=["POST"])
def set_models():
    global MODELS_STORE
    data = request.get_json()
    if data and "models" in data:
        MODELS_STORE["models"] = data["models"]
    return jsonify({"ok": True})

def build_active_models_list():
    active = [m for m in MODELS_STORE["models"] if m.get("active")]
    lines = []
    for m in active:
        until = f" — available until {m['until']}" if m.get("until") else ""
        lines.append(f"- {m['name']} ({m['country']}) — {m['cls']}{until}")
    return "\n".join(lines) if lines else "No models currently available"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        system_prompt = data.get("system", "")

        # Inject live models into system prompt
        active_list = build_active_models_list()
        system_prompt = system_prompt.replace(
            "MODELS CURRENTLY IN KUWAIT (ACTIVE ONLY):",
            "MODELS CURRENTLY IN KUWAIT (ACTIVE ONLY):\n" + active_list + "\n#END_MODELS#"
        )
        # Clean up any old model list that came from client
        if "#END_MODELS#" in system_prompt:
            parts = system_prompt.split("#END_MODELS#")
            system_prompt = parts[0] + parts[1] if len(parts) > 1 else parts[0]

        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": CLAUDE_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-6", "max_tokens": 1024, "system": system_prompt, "messages": messages},
            timeout=30
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
