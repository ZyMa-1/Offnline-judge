#include <bits/stdc++.h>
#define N 35000
#define pb push_back
#define fi first
#define se second
#define si size()
#define ll long long
#define mp make_pair
#define iter ::iterator
#define all(v) v.begin(), v.end()
#define READ(f) freopen (f, "r", stdin)
#define WRITE(f) freopen (f, "w", stdout)
#define pp pop_back
#define mapiter map<int, int>::iterator
#define pii pair<int, int>
#define forn(i, n) for(int i = 0; i < n; ++i)
#define forn1(i, n) for(int i = 0; i <= n; ++i)
#define forr(i, x, n) for(int i = x; i <= n; ++i)
#define r0 return 0
#define barnarnar ios_base::sync_with_stdio(0);cin.tie(0);cout.tie(0);
#define lld long double

const int inf = 1e9 + 1;
const ll modw = 1e9 + 7;

using namespace std;

bool ifpr(ll n)
{
    ll i = 2;
    while(i * i <= n)
    {
        if(n % i == 0)  return 0;
        i++;
    }
    return 1;
}

vector<ll> ss(ll n)
{
    ll i = 2;
    vector<ll> ans;
    ll cn = n;
    while(i * i <= cn)
    {
        if(n % i == 0 && ifpr(i))
        {
            while(n % i == 0)
            {
                ans.pb(i);
                n /= i;
            }
        }
        i++;
    }
    if(n != 1)  ans.pb(n);
    return ans;
}

int main() {
    barnarnar
    ll n;
    cin >> n;
    vector<ll> ans = ss(n);
    sort(all(ans));
    if(ans.si == 0)
    {
        cout << n;
        r0;
    }
    forn(i, ans.si)
    {
        cout << ans[i];
        if(i < ans.si - 1)  cout << ' ';
    }
    return 0;
}