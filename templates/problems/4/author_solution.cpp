#include <bits/stdc++.h>
#define N 200010
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
#define forn1(i, n) for(int i = 1; i <= n; ++i)
#define forr(i, x, n) for(int i = x; i <= n; ++i)
#define r0 return 0
#define barnarnar ios_base::sync_with_stdio(0);cin.tie(0);cout.tie(0);
#define lld long double

const int inf = 1e9 + 1;
const ll modw = 1e9 + 7;

using namespace std;

pair<int, int> v1[5 * N], v2[5 * N];
int b[N];

pair<int, int> build1(int l, int r, int u)
{
    if(l == r)
    {
        v1[u].fi = b[l];
        v1[u].se = l;
        return v1[u];
    }
    else
    {
        int m = (l + r) / 2;
        pair<int, int> t1 = build1(l, m, u * 2);
        pair<int, int> t2 = build1(m + 1, r, u * 2 + 1);
        if(t1.fi >= t2.fi)
        {
        	v1[u].fi = t1.fi;
        	v1[u].se = t1.se;
		}
		else
		{
			v1[u].fi = t2.fi;
        	v1[u].se = t2.se;
		}
        return v1[u];
    }
}

pair<int, int> get1(int l, int r, int l1, int r1, int u)
{
    if(r1 < l || l1 > r)	return mp(0, 0);
    if(l1 <= l && r <= r1)	return v1[u];
    int m = (l + r) / 2;
    pair<int, int> t1 = get1(l, m, l1, r1, u * 2), t2 = get1(m + 1, r, l1, r1, u * 2 + 1);
    if(t1.fi >= t2.fi)
    	return t1;
    else
    	return t2;
}

pair<int, int> build2(int l, int r, int u)
{
    if(l == r)
    {
        v2[u].fi = b[l];
        v2[u].se = l;
        return v2[u];
    }
    else
    {
        int m = (l + r) / 2;
        pair<int, int> t1 = build2(l, m, u * 2);
        pair<int, int> t2 = build2(m + 1, r, u * 2 + 1);
        if(t1.fi < t2.fi)
        {
        	v2[u].fi = t1.fi;
        	v2[u].se = t1.se;
		}
		else
		{
			v2[u].fi = t2.fi;
        	v2[u].se = t2.se;
		}
        return v2[u];
    }
}

pair<int, int> get2(int l, int r, int l1, int r1, int u)
{
    if(r1 < l || l1 > r)	return mp(inf, inf);
    if(l1 <= l && r <= r1)	return v2[u];
    int m = (l + r) / 2;
    pair<int, int> t1 = get2(l, m, l1, r1, u * 2), t2 = get2(m + 1, r, l1, r1, u * 2 + 1);
    if(t1.fi < t2.fi)
    	return t1;
    else
    	return t2;
}

int main()
{
	barnarnar
	int n;
	cin >> n;
	forn1(i, n)	cin >> b[i];
	build1(1, n, 1);
	build2(1, n, 1);
	int q;
	cin >> q;
	forn(i, q)
	{
		int l, r, x;
		cin >> l >> r >> x;
		pair<int, int> t1 = get1(1, n, l, r, 1), t2 = get2(1, n, l, r, 1);
		if(t1.fi != x && t1.fi != 0)
		{
			cout << t1.se << endl;
		}
		else if(t2.fi != x && t2.fi != 0)
		{
			cout << t2.se << endl;
		}
		else
		{
			cout << -1 << endl;
		}
	}
    return 0;
}