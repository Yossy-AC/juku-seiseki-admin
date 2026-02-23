# CLAUDE.md

Guidance for working with this repository.

## Project

塾成績管理システム - 生徒向けダッシュボード、講師向け管理画面、CSV一括アップロード機能を持つWeb アプリケーション。

- Student Dashboard: `public/index.html`（個人成績推移、クラス平均との比較）
- Teacher Admin Panel: `public/admin.html`（成績入力、生徒・講座管理）
- CSV Upload: `public/upload.html`（生徒・成績データの一括登録）

## Tech Stack

- Frontend: Vanilla JavaScript (ES6+), HTML5, CSS3
- Data: JSON files + localStorage キャッシング
- Deployment: Cloudflare Pages/Workers
- Local Dev: Python http.server

## Commands

```bash
npm run dev        # http://localhost:8000 で開発サーバー起動
npm run deploy     # Cloudflare へデプロイ
npm test           # テスト（未実装）
```

## Architecture

### ディレクトリ構成

```
src/
├── dataLoader.js        # JSON読み込み、キャッシング、計算処理
├── dashboard.js         # 生徒ダッシュボード
├── admin.js             # 講師管理画面
├── csvParser.js         # CSV解析
└── uploadHandler.js     # CSV アップロード処理

data/
├── students.json        # 生徒データ
├── grades.json          # 成績データ
├── classes.json         # 講座情報
└── attendance.json      # 出席記録

public/
├── index.html           # 生徒ダッシュボード
├── admin.html           # 講師管理画面
├── upload.html          # CSV アップロード
└── styles.css           # スタイル
```

### DataLoader（src/dataLoader.js）

シングルトンパターン。グローバル `dataLoader` インスタンスとして利用。

**データロード**: localStorage → JSON ファイルのフォールバック（students, grades, classes, attendance）

**主要メソッド**:
- `loadAllData()`: 生徒・成績・講座・出席データをすべて読み込む
- `getStudent(id)`, `getClass(id)`: 単一レコード取得
- `getStudentGrades(studentId)`: 生徒の成績を取得
- `calculateClassAverage(classId)`: クラス平均を計算
- `calculateStudentAverage(studentId)`: 生徒の平均を計算
- `calculateAttendanceRate(studentId)`: 出席率を計算

**データ形式**:
```javascript
// students.json
{ "students": [{ id, name, classId, joinDate }, ...] }

// grades.json（新フォーマット）
{
  "grades": [{
    id, studentId, classId, date, lessonNumber, lessonContent,
    scores: { comprehension, unseenProblems, grammar, vocabulary, listening, total },
    maxScores: { comprehension: 20, ..., total: 100 }
  }, ...]
}

// attendance.json
{ "attendance": [{ id, studentId, date, status }, ...] }
```

### UI

**ダッシュボード**:
- URL パラメータ `?studentId=s001` で生徒指定
- DOMContentLoaded で dataLoader.loadAllData() 実行、ダッシュボード表示

**管理画面**:
- タブベースUI（`.tab-btn[data-tab]` で切り替え）
- 講座選択時にフィルタリング

**CSV アップロード**:
- parseNewFormatCSV() で「【生徒データ】」「【チェックテスト成績】」セクションを自動判別
- 生徒名でマッチング、成績を生徒ID にリンク
- localStorage に保存（studentData, gradeData キー）

## Key Details

**CSV フォーマット**:
```
【生徒データ】セクション
教室,氏名,ｼﾒｲ,性,高校,学科,学校ｸﾗｽ,部活,志望大学,志望学部

【チェックテスト成績】セクション
氏名,授業回,授業内容,日付,授業内容の理解,初見問題,文法語法,単語,リスニング,合計
```

**データ永続化**:
- JSON ファイルが真実のソース
- loadAllData() で一度読み込んでキャッシュ
- ユーザー編集は localStorage に保存
- 本番（Cloudflare D1）への永続化は Phase 2

**グレード形式対応**:
- 従来フォーマット: `{ score, maxScore }`
- 新フォーマット: `{ scores: { total, ... }, maxScores: { total, ... } }`
- 両形式を 0-100 スケールに正規化

**エラーハンドリング**:
- ネットワークエラー: alert + console.error
- 欠損データ: null/空配列で安全に処理
- URL パラメータ欠落: 最初の生徒にフォールバック

## Development Notes

- ビルドステップなし（ Vanilla JS）
- 相対パスは `/public/` ディレクトリからアクセスを前提
- localStorage キーは uploadHandler と dataLoader で一致させる必須
- Cloudflare デプロイは wrangler CLI で認証が必要
