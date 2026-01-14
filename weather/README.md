# 天気予報アプリ 🌤️

東京の天気情報をリアルタイムで表示するシンプルなWebアプリケーションです。

## 使用技術

- **バックエンド**: Python (Flask)
- **API**: OpenWeatherMap API (無料版)
- **フロントエンド**: HTML5 / CSS3
- **デプロイ**: Render.com

## 機能

- 東京の現在の気温・天気・湿度を表示
- 体感温度の表示
- レスポンシブデザイン対応
- エラーハンドリング

## セットアップ手順

### 1. ローカル開発環境の構築

```bash
# 依存パッケージのインストール
pip install -r requirements.txt
```

### 2. OpenWeatherMap APIキーの取得

1. https://openweathermap.org/api にアクセス
2. 無料プランで登録
3. APIキーを取得

### 3. 環境変数の設定（2通り）

- 方式A: `.env` ファイルを作成（推奨）

```
OPENWEATHER_API_KEY=your_api_key_here
```

- 方式B: PowerShellで一時的に設定（Windows）

```powershell
$env:OPENWEATHER_API_KEY="your_api_key_here"
python app.py
```

### 4. ローカルで実行

```bash
python app.py
```

ブラウザで http://localhost:5000 にアクセス

## Render.comへのデプロイ手順

### 1. リポジトリの準備

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Render.comで新規Webサービスを作成

1. [Render.com](https://render.com) にログイン
2. 「New」→「Web Service」をクリック
3. GitHubリポジトリを接続
4. 以下の設定を確認：
   - **Name**: weather-app
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. 環境変数の設定

Render.comのダッシュボードで以下を追加：

```
OPENWEATHER_API_KEY=your_api_key_here
```

### 4. デプロイ

「Deploy」ボタンをクリック

## ファイル構成

```
weather/
├── app.py                 # Flaskアプリケーション
├── requirements.txt       # Python依存パッケージ
├── Procfile              # Renderデプロイ設定
├── .env                  # 環境変数（ローカル用）
├── .gitignore           # Gitignore設定
├── templates/
│   └── index.html        # HTMLテンプレート
└── static/
    └── style.css         # スタイルシート
```

## アピールポイント

✅ **API連携の基礎**: 外部APIを活用したデータ取得
✅ **JSONデータの処理**: APIレスポンスの解析とテンプレートへの渡し方
✅ **Flask実装**: Pythonフレームワークの基本的な使用法
✅ **レスポンシブデザイン**: モバイル対応のUI
✅ **エラーハンドリング**: 例外処理の実装
✅ **本番環境デプロイ**: Render.comでの実際の運用

## トラブルシューティング

### APIキーエラー
→ `.env` に正しいキーがあるか、または PowerShell の環境変数に設定してから再起動してください。

### 7日間予報が5日しか出ない
→ OpenWeatherのOne Call API(3.0)はプランによって制限があります。7日が取得できない場合は自動的に5日間予報にフォールバックします。

### 天気情報が表示されない
→ Render.comの「Logs」を確認してエラーメッセージを確認してください

## 今後の拡張案

- [ ] 複数都市の対応
- [ ] 天気予報（5日間など）
- [ ] 地図表示
- [ ] 多言語対応
- [ ] データベース対応

## ライセンス

MIT License

## 参考資料

- [Flask公式ドキュメント](https://flask.palletsprojects.com/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Render.comドキュメント](https://docs.render.com/)
