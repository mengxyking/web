"""
填充近 30 天历史数据，用于折线图演示。
运行：/usr/local/bin/python3.9 seed_history.py
"""
import random
from datetime import date, timedelta, datetime

from run import create_app
from models import db, Product, ComputerDevice, PhoneDevice, DailyOnline

app = create_app()

with app.app_context():
    today = date.today()

    products = Product.query.all()
    print(f'找到 {len(products)} 个产品')

    for product in products:
        print(f'\n[{product.name}] 开始填充...')

        # 每个产品预先创建 5~8 台固定电脑设备
        n_computers = random.randint(5, 8)
        computers = []
        for i in range(n_computers):
            code = f'COMP-{product.id}-{i+1:03d}'
            comp = ComputerDevice.query.filter_by(
                device_code=code, product_id=product.id
            ).first()
            if not comp:
                comp = ComputerDevice(
                    device_code=code, product_id=product.id,
                    first_seen=datetime(2026, 1, 1),
                    last_seen=datetime(2026, 1, 1),
                )
                db.session.add(comp)
                db.session.flush()
            computers.append(comp)

        # 每台电脑对应 3~8 台固定手机
        phone_pool = {}   # comp_id -> [PhoneDevice]
        for comp in computers:
            n_phones = random.randint(3, 8)
            phones = []
            for j in range(n_phones):
                code = f'PHONE-{product.id}-{comp.id}-{j+1:03d}'
                phone = PhoneDevice.query.filter_by(
                    device_code=code, computer_device_id=comp.id
                ).first()
                if not phone:
                    phone = PhoneDevice(
                        device_code=code,
                        computer_device_id=comp.id,
                        product_id=product.id,
                        first_seen=datetime(2026, 1, 1),
                        last_seen=datetime(2026, 1, 1),
                    )
                    db.session.add(phone)
                    db.session.flush()
                phones.append(phone)
            phone_pool[comp.id] = phones

        db.session.commit()

        # 为过去 30 天（不含今天）逐日写 DailyOnline
        inserted = 0
        for offset in range(30, 0, -1):
            day = today - timedelta(days=offset)

            # 当天随机选几台电脑在线（至少 2 台）
            online_comps = random.sample(computers, k=random.randint(2, len(computers)))

            for comp in online_comps:
                pool = phone_pool[comp.id]
                # 每台在线电脑随机带几台手机
                online_phones = random.sample(pool, k=random.randint(1, len(pool)))

                for phone in online_phones:
                    exists = DailyOnline.query.filter_by(
                        product_id=product.id,
                        computer_device_id=comp.id,
                        phone_device_id=phone.id,
                        date=day,
                    ).first()
                    if not exists:
                        db.session.add(DailyOnline(
                            product_id=product.id,
                            computer_device_id=comp.id,
                            phone_device_id=phone.id,
                            date=day,
                            first_seen_at=datetime.combine(day, datetime.min.time()),
                        ))
                        inserted += 1

        db.session.commit()
        print(f'  插入 {inserted} 条 DailyOnline 记录')

    print('\n完成！')
