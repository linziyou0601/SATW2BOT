CONFIG = {
    "DB_HOST": "127.0.0.1",
    "DB_USER": "satw2",
    "DB_PASSWORD": "satw2satw2",
    "DB_DATABASE": "satw2bot",

    "DB_CREATE_TABLE": '''
    CREATE TABLE IF NOT EXISTS line_user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        channel_id TEXT NOT NULL COMMENT "頻道 ID",
        account TEXT COMMENT "網站帳號",
        draw_coupon TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        bind TINYINT DEFAULT 0 COMMENT "0=未綁定, 1=已綁定",
        mute TINYINT DEFAULT 0 COMMENT "0=可以聊天, 1=安靜",
        global_talk TINYINT DEFAULT 1 COMMENT "0=這裡教的話, 1=所有人教的話",
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS line_statement (
        id INT AUTO_INCREMENT PRIMARY KEY,
        keyword TEXT NOT NULL COMMENT "關鍵字",
        response TEXT NOT NULL COMMENT "回覆內容",
        channel_id TEXT COMMENT "建立者頻道 ID",
        user_id TEXT COMMENT "建立者 ID",
        checked TEXT COMMENT "可疑詞標記",
        priority INT DEFAULT 4 COMMENT "詞條優先度",
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS line_replied (
        id INT AUTO_INCREMENT PRIMARY KEY,
        type TEXT NOT NULL COMMENT "訊息種類",
        message TEXT NOT NULL COMMENT "訊息內容",
        valid TINYINT NOT NULL COMMENT "0=功能型, 1=關鍵字, 2=一般型",
        channel_id TEXT NOT NULL COMMENT "發送至頻道 ID",
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS line_received (
        id INT AUTO_INCREMENT PRIMARY KEY,
        type TEXT NOT NULL COMMENT "訊息種類",
        message TEXT NOT NULL COMMENT "訊息內容",
        channel_id TEXT NOT NULL COMMENT "發送者頻道 ID",
        user_id TEXT NOT NULL COMMENT "發送者 ID",
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS line_pushed (
        id INT AUTO_INCREMENT PRIMARY KEY,
        type TEXT NOT NULL COMMENT "訊息種類",
        title TEXT NOT NULL COMMENT "訊息標題",
        message TEXT NOT NULL COMMENT "訊息內容",
        channel_id TEXT NOT NULL COMMENT "發送至頻道 ID",
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS line_postfix (
        id INT AUTO_INCREMENT PRIMARY KEY,
        start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT "啟始日期",
        last_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT "結束日期",
        content TEXT NOT NULL COMMENT "後綴內容",
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS line_temp_statement (
        id INT AUTO_INCREMENT PRIMARY KEY,
        keyword TEXT NOT NULL COMMENT "關鍵字",
        response TEXT NOT NULL COMMENT "回覆內容",
        channel_id TEXT COMMENT "建立者頻道 ID",
        user_id TEXT COMMENT "建立者 ID",
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS line_location (
        id INT AUTO_INCREMENT PRIMARY KEY,
        address TEXT NOT NULL COMMENT "地址",
        lat double NOT NULL COMMENT '經度',
        lng double NOT NULL COMMENT '緯度',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS api_key (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name TEXT NOT NULL COMMENT "金鑰名稱",
        secret TEXT NOT NULL COMMENT '金鑰',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
}

def ENV(key, default=None):
    return CONFIG.get(key, default)