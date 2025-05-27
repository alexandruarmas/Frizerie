import sqlite3

def check_dangling_references():
    conn = sqlite3.connect('frizerie.db')
    cursor = conn.cursor()

    print('Checking for dangling stylist_id in analytics_events...')
    cursor.execute('''
        SELECT id, stylist_id FROM analytics_events
        WHERE stylist_id IS NOT NULL AND stylist_id NOT IN (SELECT id FROM users)
    ''')
    stylists = cursor.fetchall()
    if stylists:
        print('Dangling stylist_id found in analytics_events:')
        for row in stylists:
            print(f'  analytics_event id={row[0]}, stylist_id={row[1]}')
    else:
        print('No dangling stylist_id found.')

    print('\nChecking for dangling service_id in analytics_events...')
    cursor.execute('''
        SELECT id, service_id FROM analytics_events
        WHERE service_id IS NOT NULL AND service_id NOT IN (SELECT id FROM services)
    ''')
    services = cursor.fetchall()
    if services:
        print('Dangling service_id found in analytics_events:')
        for row in services:
            print(f'  analytics_event id={row[0]}, service_id={row[1]}')
    else:
        print('No dangling service_id found.')

    print('\nChecking for dangling booking_id in analytics_events...')
    cursor.execute('''
        SELECT id, booking_id FROM analytics_events
        WHERE booking_id IS NOT NULL AND booking_id NOT IN (SELECT id FROM bookings)
    ''')
    bookings = cursor.fetchall()
    if bookings:
        print('Dangling booking_id found in analytics_events:')
        for row in bookings:
            print(f'  analytics_event id={row[0]}, booking_id={row[1]}')
    else:
        print('No dangling booking_id found.')

    conn.close()

if __name__ == '__main__':
    check_dangling_references() 