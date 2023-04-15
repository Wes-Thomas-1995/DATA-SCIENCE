from sqlalchemy import create_engine
import psycopg2








def CREATE_TABLES():

    try:

        conn = psycopg2.connect(host="XXXXX",
                                port=XXXXX,
                                database="XXXXX",
                                user="XXXXX",
                                password="XXXXX")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE test_portfolio_history (
                    TICKER_COMMANDS VARCHAR(255) NOT NULL,
                    PORTFOLIO_COMMANDS VARCHAR(255) NOT NULL,
                    PRICE FLOAT NOT NULL,
                    QUANTITY FLOAT NOT NULL,
                    INDUSTRY VARCHAR(255) NOT NULL,
                    SECTOR VARCHAR(255) NOT NULL,                
                    NAME VARCHAR(255) NOT NULL,
                    DATE DATE NOT NULL DEFAULT CURRENT_DATE,
                    UPDATED VARCHAR(255) NOT NULL DEFAULT 'NO'
            )
            """)
        cur.close()
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return


CREATE_TABLES()