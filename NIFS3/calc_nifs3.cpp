#include <bits/stdc++.h>
using namespace std;

// find NIFS3
double calc_nifs3(double X, vector<double>& x0, vector<double>& y0, vector<double>& M){
    int k = 1;
    while(x0[k] < X) k++;

    return (1/(x0[k]-x0[k-1]))
            * (M[k-1]*pow(x0[k] - X, 3)/6.
            +  M[k] * pow(X - x0[k-1], 3)/6. 
            + (y0[k-1] - M[k-1]*pow(x0[k]-x0[k-1], 2)/6.)*(x0[k]-X)
            + (y0[k] - M[k]*pow(x0[k]-x0[k-1], 2)/6.)*(X-x0[k-1]));
}


// helper functions
double lambda(int k, vector<double>& x){
    return (x[k] - x[k-1])/(x[k+1] - x[k-1]);
}

double dk(int k, vector<double>& x, vector<double>& y){
    double t1 = (y[k+1] - y[k])/(x[k+1] - x[k]);
    double t2 = (y[k] - y[k-1])/(x[k] - x[k-1]);
    return 6 * (t1 - t2)/(x[k+1] - x[k-1]);
}

// fins M (moments)
vector<double> calc_moments(vector<double>& x, vector<double>& y){
    int n = x.size()-1;
    vector<double> q, p, u, M;
    q.reserve(n), p.reserve(n), u.reserve(n), M.resize(n+1);
    q.push_back(0), p.push_back(0), u.push_back(0);

    for(int k = 1; k <= n-1; k++){
        double lk = lambda(k, x);
        p.push_back(lk * q[k-1] + 2);
        q.push_back((lk-1)/p[k]);
        u.push_back((dk(k, x, y) - lk * u[k-1])/p[k]);
    }

    M[n] = 0;
    M[n-1] = u[n-1];
    for(int k = n-2; k >= 0; k--){
        M[k] = u[k] + q[k] * M[k+1];
    }

    return M;
}


// ------------------ main ------------------
int main(int argc, char** argv){        // filename, ([n])
    int n = 0;
    vector<double> t;
    vector<double> x;
    vector<double> y;

    // ----- fill up x and y tables -----
    cin >> n;
    double a, b;
    for(int i = 0; i < n; i++){
        cin >> a >> b;
        x.push_back(a);
        y.push_back(b);
    }
    n -= 1;
    
    // ----- fill up t table -----
    for(int k = 0; k <= n; k++){
        t.push_back(k/(double)n);
    }

    // ----- take care of moments -----
    vector<double> Mx = calc_moments(t, x);
    vector<double> My = calc_moments(t, y);

    // ----- calculate NIFS3 -----
    for(double T = t[0]; T <= t[n]; T += 0.001){
        cout << calc_nifs3(T, t, x, Mx) << ' ' << calc_nifs3(T, t, y, My) << '\n';
    }
}
