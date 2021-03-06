#include <bits/stdc++.h>
#define N 100010
#define fi first
#define se second
#define ll long long

using namespace std;

ll b[N];
ll v[5 * N];


ll build(ll l, ll r, ll u)
{
    if(l == r)	v[u] = b[l];
    else
    {
        ll m = (l + r) / 2;
        v[u] = build(l, m, u * 2) + build(m + 1, r, u * 2 + 1);
    }
    return v[u];
}

ll get(ll l, ll r, ll l1, ll r1, ll u)
{
    if(r1 < l || l1 > r)	return 0ll;
    if(l1 <= l && r <= r1)	return v[u];
    ll m = (l + r) / 2;
	return get(l, m, l1, r1, u * 2) + get(m + 1, r, l1, r1, u * 2 + 1);
}

int main()
{
    ll n;
    cin >> n;
    for(int i = 1; i <= n; i++)	cin >> b[i];
    build(1, n, 1);
    ll q;
    cin >> q;
    for(int i = 0; i < q; i++)
    {
    	ll l, r;
    	cin >> l >> r;
    	cout << get(1, n, l, r, 1) << endl;
	}
    return 0;
}