from app import app

def run_test():
    with app.test_client() as c:
        # successful login
        res = c.post('/api/login', json={'username':'admin', 'password':'1234'})
        print('LOGIN ->', res.status_code, res.get_json())
        print('SET-COOKIE ->', res.headers.get('Set-Cookie'))

        # access messages with same client (preserves session cookie)
        res2 = c.get('/api/messages')
        print('MESSAGES ->', res2.status_code)
        print(res2.get_json())

        # failed login
        res3 = c.post('/api/login', json={'username':'bad', 'password':'wrong'})
        print('BAD LOGIN ->', res3.status_code, res3.get_json())

if __name__ == '__main__':
    run_test()
