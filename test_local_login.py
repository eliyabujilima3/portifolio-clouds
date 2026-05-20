from backend.app import app

def run_test():
    with app.test_client() as c:
        res = c.post('/api/login', json={'username':'admin', 'password':'1234'})
        print('LOGIN ->', res.status_code, res.get_json())
        print('SET-COOKIE ->', res.headers.get('Set-Cookie'))

        res2 = c.get('/api/messages')
        print('MESSAGES ->', res2.status_code)
        print(res2.get_json())

if __name__ == '__main__':
    run_test()
