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
            CREATE TABLE ucts_trade_history_portfolio (
                    STRATEGY VARCHAR(255) NOT NULL,
                    ORDERID VARCHAR(255) NOT NULL,
                    TRADE_DATE DATE NOT NULL DEFAULT CURRENT_DATE,
                    SYMBOL VARCHAR(255) NOT NULL,
                    SIDE VARCHAR(255) NOT NULL,                
                    PRICE FLOAT NOT NULL,
                    QTY FLOAT NOT NULL,
                    USDT_VALUE FLOAT NOT NULL,
                    COMMISSION_ASSET VARCHAR(255) NOT NULL,
                    COMMISSION FLOAT NOT NULL
            )
            """)
        cur.close()
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()



    try:

        conn = psycopg2.connect(host="XXXXX",
                                port=XXXXX,
                                database="XXXXX",
                                user="XXXXX",
                                password="XXXXX")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE ucts_portfolio_balance_history (
                    TRADE_DATE DATE NOT NULL DEFAULT CURRENT_DATE,
                    USDT_VALUE FLOAT NOT NULL
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