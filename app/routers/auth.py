from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from app.auth import authenticate_admin, clear_session

router = APIRouter()

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, password: str = ""):
    """ログイン処理"""
    # フォームからパスワードを取得
    form_data = await request.form()
    password = form_data.get("password", "")

    if not password:
        return """
        <div style="background: #ffebee; color: #c62828; padding: 1rem; border-radius: 8px; text-align: center;">
            <p><strong>エラー:</strong> パスワードを入力してください</p>
            <p style="margin-top: 1rem;"><a href="/login" style="color: #0066cc; text-decoration: underline;">ログイン画面に戻る</a></p>
        </div>
        """

    # パスワード検証
    if authenticate_admin(password):
        # セッションにフラグを設定
        request.session["authenticated"] = True
        request.session["login_time"] = datetime.now().isoformat()

        # 管理画面にリダイレクト
        return RedirectResponse(url="/admin", status_code=302)
    else:
        # パスワード間違い
        return """
        <html>
            <head>
                <meta charset="UTF-8">
                <title>ログイン失敗</title>
                <link rel="stylesheet" href="/static/css/styles.css">
            </head>
            <body>
                <div class="login-container">
                    <div class="login-card">
                        <div style="background: #ffebee; color: #c62828; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                            <p style="margin: 0;"><strong>パスワードが正しくありません</strong></p>
                        </div>
                        <p><a href="/login" style="color: #0066cc; text-decoration: underline;">もう一度ログイン</a></p>
                    </div>
                </div>
            </body>
        </html>
        """

@router.post("/logout")
async def logout(request: Request):
    """ログアウト処理"""
    # セッションをクリア
    clear_session(request.session)

    # ログイン画面にリダイレクト
    return RedirectResponse(url="/login", status_code=302)
