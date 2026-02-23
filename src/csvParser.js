// ===== CSV パーサー =====

class CSVParser {
    // CSV テキストを解析
    static parseCSV(text) {
        const lines = text.trim().split('\n');
        if (lines.length < 2) {
            throw new Error('CSVファイルが空です');
        }

        // ヘッダーを取得
        const headers = this.parseCSVLine(lines[0]);
        console.log('Headers:', headers);

        // データ行を解析
        const data = [];
        for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim() === '') continue;

            const values = this.parseCSVLine(lines[i]);
            const row = {};

            headers.forEach((header, index) => {
                row[header] = values[index] || '';
            });

            data.push(row);
        }

        return data;
    }

    // 1行を解析（カンマで分割、引用符内のカンマは除外）
    static parseCSVLine(line) {
        const result = [];
        let current = '';
        let insideQuotes = false;

        for (let i = 0; i < line.length; i++) {
            const char = line[i];

            if (char === '"') {
                insideQuotes = !insideQuotes;
            } else if (char === ',' && !insideQuotes) {
                result.push(current.trim().replace(/^"|"$/g, ''));
                current = '';
            } else {
                current += char;
            }
        }

        result.push(current.trim().replace(/^"|"$/g, ''));
        return result;
    }

    // Excel ファイルを CSV に変換（簡易版）
    static async excelToCSV(file) {
        // 注：実装は複雑なため、説明のみ
        // 本来は SheetJS 等のライブラリを使用
        if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
            alert('Excel ファイルは Calc/Numbers で CSV 保存してからアップロードしてください');
            return null;
        }

        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    // テンプレート CSV を生成
    static generateTemplate() {
        // 生徒データセクション
        let csv = '【生徒データ】セクション\n';
        csv += '生徒コード,教室,氏名,シメイ,性,高校,学科,学校クラス,部活,志望大学,志望学部\n';
        csv += 's001,難関大クラス,田中太郎,たなかたろう,男,県立第一高校,理系,3-A,英語部,東京大学,工学部\n';
        csv += 's002,難関大クラス,鈴木花子,すずきはなこ,女,県立女子高校,文系,3-B,演劇部,京都大学,文学部\n';
        csv += '\n';

        // チェックテスト成績セクション
        csv += '【チェックテスト成績】セクション\n';
        csv += '氏名,授業回,授業内容,日付,授業内容の理解,初見問題,文法語法,単語,リスニング,合計\n';
        csv += '田中太郎,1,文法基礎：時制,2026-02-02,18,16,19,17,15,85\n';
        csv += '田中太郎,2,長文読解：社会評論,2026-02-09,19,18,16,19,17,89\n';
        csv += '鈴木花子,1,文法基礎：時制,2026-02-02,20,19,20,19,18,96\n';

        return csv;
    }

    // CSV を生ダウンロード
    static downloadCSV(filename, csv) {
        const blob = new Blob([csv], { type: 'text/csv; charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);

        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}
