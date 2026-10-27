#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int N, K;
    cin >> N >> K;

    vector<long long> A(N);

    for (int i = 0; i < N; i++) {
        cin >> A[i];
    }

    long long topSum = 0;
    long long bottomSum = 0;
    long long maximumSum = 0;

    // Initially take K elements from the top
    for (int i = 0; i < K; i++) {
        topSum += A[i];
    }

    maximumSum = topSum;

    // Replace top elements one by one with bottom elements
    for (int i = 1; i <= K; i++) {
        topSum -= A[K - i];
        bottomSum += A[N - i];

        maximumSum = max(maximumSum, topSum + bottomSum);
    }

    cout << maximumSum << endl;

    return 0;
}