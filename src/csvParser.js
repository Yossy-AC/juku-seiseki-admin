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
        const headers = ['氏名', '高校', '性別', '学年', '志望大学', '講座ID'];
        const sample = [
            ['田中太郎', '県立第一高校', '男', '3', '東京大学', 'class001'],
            ['鈴木花子', '県立女子高校', '女', '3', '京都大学', 'class001'],
            ['佐藤次郎', '私立東京高校', '男', '2', '大阪大学', 'class003']
        ];

        let csv = headers.map(h => `"${h}"`).join(',') + '\n';
        csv += sample.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');

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
