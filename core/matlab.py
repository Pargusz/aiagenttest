"""MATLAB / GNU Octave kod ureteci.

Fizik problemleri icin calisir durumda kod uretir. Uretilen kodlar hem MATLAB
hem Octave ile uyumludur (Octave ucretsizdir).
"""
import re

from . import solver


def _hdr(title_tr, title_en, lang="tr"):
    t = title_tr if lang == "tr" else title_en
    return "%% %s\n%% ParguszPhysics tarafindan uretildi\n\n" % t


TEMPLATES = {}


def tpl(key, tr, en, kw, code, notes_tr="", notes_en=""):
    TEMPLATES[key] = {"tr": tr, "en": en, "kw": kw.split("|"), "code": code,
                      "notes_tr": notes_tr, "notes_en": notes_en}


tpl("egik_atis", "Egik atis (projektil hareketi)", "Projectile motion",
    "egik atis|projektil|atis|menzil|projectile|trajectory|launch",
    r"""clear; clc; close all;

%% --- Parametreler ---
v0    = 25;          % ilk hiz [m/s]
theta = 45;          % atis acisi [derece]
h0    = 0;           % baslangic yuksekligi [m]
g     = 9.81;        % yercekimi ivmesi [m/s^2]

%% --- Analitik cozum ---
th  = deg2rad(theta);
vx  = v0*cos(th);
vy0 = v0*sin(th);

% Ucus suresi: h0 + vy0*t - g*t^2/2 = 0  -> ikinci derece denklem
t_flight = (vy0 + sqrt(vy0^2 + 2*g*h0))/g;
t = linspace(0, t_flight, 500);

x = vx.*t;
y = h0 + vy0.*t - 0.5*g.*t.^2;

R    = vx*t_flight;             % menzil
Hmax = h0 + vy0^2/(2*g);        % maksimum yukseklik

fprintf('Ucus suresi : %.3f s\n', t_flight);
fprintf('Menzil      : %.3f m\n', R);
fprintf('Maks. yuks. : %.3f m\n', Hmax);

%% --- Grafik ---
figure('Color','w');
plot(x, y, 'LineWidth', 2); hold on; grid on;
plot(R, 0, 'ro', 'MarkerFaceColor','r');
plot(vx*vy0/g, Hmax, 'gs', 'MarkerFaceColor','g');
xlabel('Yatay mesafe x [m]'); ylabel('Yukseklik y [m]');
title(sprintf('Egik Atis: v_0 = %.1f m/s, \\theta = %.0f^\\circ', v0, theta));
legend('Yorunge','Carpma noktasi','Tepe noktasi','Location','best');
axis equal;
""",
    "Hava direnci ihmal edilmistir. Direnc eklemek isterseniz ode45 ile "
    "sayisal cozume gecmek gerekir.",
    "Air resistance is neglected; adding drag requires a numerical solution with ode45.")

tpl("sonumlu_osilator", "Sonumlu harmonik osilator (ode45)",
    "Damped harmonic oscillator (ode45)",
    "sonumlu|osilator|harmonik|yay|titresim|damped|oscillator|spring|ode45",
    r"""clear; clc; close all;

%% --- Parametreler ---
m     = 1.0;      % kutle [kg]
k     = 50;       % yay sabiti [N/m]
b     = 0.5;      % sonum katsayisi [N.s/m]
x0    = 0.2;      % ilk konum [m]
v0    = 0;        % ilk hiz [m/s]
tspan = [0 20];

w0    = sqrt(k/m);              % dogal acisal frekans
zeta  = b/(2*sqrt(m*k));        % sonum orani

fprintf('Dogal frekans w0 = %.3f rad/s (f0 = %.3f Hz)\n', w0, w0/(2*pi));
fprintf('Sonum orani zeta = %.4f -> ', zeta);
if zeta < 1,      fprintf('az sonumlu\n');
elseif zeta == 1, fprintf('kritik sonumlu\n');
else,             fprintf('asiri sonumlu\n');
end

%% --- Sayisal cozum ---
% x'' + (b/m)x' + (k/m)x = 0  ->  y = [x; x']
f = @(t,y) [ y(2); -(b/m)*y(2) - (k/m)*y(1) ];
opts = odeset('RelTol',1e-9,'AbsTol',1e-11);
[t, y] = ode45(f, tspan, [x0; v0], opts);

x = y(:,1);  v = y(:,2);
E = 0.5*m*v.^2 + 0.5*k*x.^2;     % toplam mekanik enerji

%% --- Grafikler ---
figure('Color','w');
subplot(3,1,1);
plot(t, x, 'LineWidth', 1.5); grid on;
hold on;
if zeta < 1
    env = x0*exp(-zeta*w0*t);
    plot(t,  env, 'r--', t, -env, 'r--');
    legend('x(t)','Zarf e^{-\zeta\omega_0 t}','Location','best');
end
ylabel('Konum [m]'); title('Sonumlu Harmonik Osilator');

subplot(3,1,2);
plot(t, v, 'LineWidth', 1.5); grid on;
ylabel('Hiz [m/s]');

subplot(3,1,3);
plot(t, E, 'LineWidth', 1.5); grid on;
ylabel('Enerji [J]'); xlabel('Zaman [s]');

figure('Color','w');
plot(x, v, 'LineWidth', 1.2); grid on;
xlabel('x [m]'); ylabel('v [m/s]'); title('Faz Uzayi');
axis equal;
""",
    "Enerji grafigi hem fizigi gosterir hem de sayisal cozumun dogrulugunu "
    "kontrol etmenizi saglar: b = 0 yaparsaniz enerji sabit kalmalidir.",
    "The energy plot both shows the physics and validates the solver: with b = 0 it must stay flat.")

tpl("sarkac", "Sarkac (dogrusal olmayan, buyuk aci)",
    "Pendulum (nonlinear, large angle)",
    "sarkac|pendulum|buyuk aci|nonlinear|dogrusal olmayan",
    r"""clear; clc; close all;

%% --- Parametreler ---
L  = 1.0;        % ip uzunlugu [m]
g  = 9.81;
th0_deg = [5 30 90 170];   % karsilastirilacak baslangic acilari
tspan = [0 10];

T_kucuk = 2*pi*sqrt(L/g);   % kucuk aci yaklasimindaki periyot
fprintf('Kucuk aci periyodu: %.4f s\n', T_kucuk);

figure('Color','w'); hold on; grid on;
for th0 = th0_deg
    y0 = [deg2rad(th0); 0];
    f  = @(t,y) [ y(2); -(g/L)*sin(y(1)) ];       % TAM denklem (sin, theta degil)
    [t, y] = ode45(f, tspan, y0, odeset('RelTol',1e-10,'AbsTol',1e-12));
    plot(t, rad2deg(y(:,1)), 'LineWidth', 1.4, ...
         'DisplayName', sprintf('\\theta_0 = %d^\\circ', th0));

    % Gercek periyodu sifir gecislerinden olc
    s = sign(y(:,1));
    idx = find(s(1:end-1) ~= s(2:end));
    if numel(idx) >= 3
        T_gercek = 2*(t(idx(3)) - t(idx(1)))/2;
        fprintf('theta0 = %3d deg -> T = %.4f s  (sapma %%%.2f)\n', ...
                th0, T_gercek, 100*(T_gercek-T_kucuk)/T_kucuk);
    end
end
xlabel('Zaman [s]'); ylabel('Aci [derece]');
title('Sarkac: Genlik Periyodu Nasil Etkiler');
legend('Location','best');
""",
    "Kucuk acida periyot genlikten bagimsizdir, ama 90 derecede yaklasik %18, "
    "170 derecede %100'den fazla sapma olur. Cikti bunu sayisal olarak gosterir.",
    "At small angles the period is amplitude-independent, but it deviates ~18% at 90° and over 100% at 170°.")

tpl("fft", "FFT ile frekans analizi", "FFT frequency analysis",
    "fft|frekans analizi|spektrum|sinyal|fourier|spectrum|signal",
    r"""clear; clc; close all;

%% --- Sentetik sinyal (kendi verinizle degistirin) ---
fs = 1000;                 % ornekleme frekansi [Hz]
T  = 2;                    % sure [s]
t  = (0:1/fs:T-1/fs)';
N  = numel(t);

y = 1.0*sin(2*pi*50*t) + 0.5*sin(2*pi*120*t) + 0.2*randn(N,1);

%% --- FFT ---
Y = fft(y);
P2 = abs(Y/N);             % iki tarafli genlik spektrumu
P1 = P2(1:floor(N/2)+1);   % tek tarafli
P1(2:end-1) = 2*P1(2:end-1);
f = fs*(0:floor(N/2))'/N;

%% --- Baskin frekanslari bul ---
[pks, locs] = sort(P1, 'descend');
fprintf('En guclu 3 bilesen:\n');
for i = 1:3
    fprintf('  f = %7.2f Hz   genlik = %.4f\n', f(locs(i)), pks(i));
end

%% --- Grafikler ---
figure('Color','w');
subplot(2,1,1);
plot(t(1:min(500,N)), y(1:min(500,N))); grid on;
xlabel('Zaman [s]'); ylabel('Genlik'); title('Zaman Alani');

subplot(2,1,2);
plot(f, P1, 'LineWidth', 1.2); grid on;
xlabel('Frekans [Hz]'); ylabel('|P1(f)|'); title('Tek Tarafli Genlik Spektrumu');
xlim([0 fs/2]);
""",
    "Frekans cozunurlugu df = fs/N'dir. Iki yakin frekansi ayirmak icin daha uzun "
    "kayit gerekir; ornekleme hizini artirmak bu konuda yardimci olmaz.",
    "Frequency resolution is df = fs/N. Separating close peaks needs a longer record, not a higher sampling rate.")

tpl("isi_denklemi", "Isi denklemi (1B, sonlu farklar)",
    "Heat equation (1D, finite differences)",
    "isi denklemi|difuzyon|sonlu fark|pde|heat equation|diffusion|finite difference",
    r"""clear; clc; close all;

%% --- Fiziksel parametreler ---
L     = 1.0;        % cubuk uzunlugu [m]
alpha = 1e-4;       % isil yayinim [m^2/s]
Tson  = 2000;       % simulasyon suresi [s]

%% --- Ayriklastirma ---
Nx = 101;
dx = L/(Nx-1);
x  = linspace(0, L, Nx)';

% KARARLILIK KOSULU (acik yontem icin zorunlu):  r = alpha*dt/dx^2 <= 0.5
dt = 0.4*dx^2/alpha;
Nt = round(Tson/dt);
r  = alpha*dt/dx^2;
fprintf('dt = %.4f s, r = %.3f (kararlilik icin <= 0.5 olmali)\n', dt, r);

%% --- Baslangic ve sinir kosullari ---
u = zeros(Nx,1);
u(x > 0.4 & x < 0.6) = 100;    % ortada sicak bolge
u(1) = 0; u(end) = 0;          % uclar sabit 0 C (Dirichlet)

snapshots = round(linspace(1, Nt, 6));
figure('Color','w'); hold on; grid on;
plot(x, u, 'k', 'LineWidth', 2, 'DisplayName', 't = 0 s');

for n = 1:Nt
    u_new = u;
    u_new(2:end-1) = u(2:end-1) + r*(u(3:end) - 2*u(2:end-1) + u(1:end-2));
    u_new(1) = 0; u_new(end) = 0;
    u = u_new;
    if ismember(n, snapshots)
        plot(x, u, 'LineWidth', 1.4, ...
             'DisplayName', sprintf('t = %.0f s', n*dt));
    end
end

xlabel('Konum x [m]'); ylabel('Sicaklik [^\circC]');
title('1B Isi Denklemi - Acik Sonlu Farklar');
legend('Location','best');
""",
    "r > 0.5 olursa cozum patlar. Daha buyuk adim kullanmak isterseniz ortuk "
    "(implicit, Crank-Nicolson) yonteme gecin.",
    "If r > 0.5 the solution blows up. For larger steps switch to an implicit (Crank-Nicolson) scheme.")

tpl("kuantum_kuyu", "Kuantum kuyusu (Schrodinger, sayisal)",
    "Quantum well (numerical Schrodinger)",
    "kuantum kuyu|schrodinger|enerji duzeyi|dalga fonksiyonu|quantum well|eigenstate",
    r"""clear; clc; close all;

%% --- Sabitler (SI) ---
hbar = 1.054571817e-34;
me   = 9.1093837139e-31;
eV   = 1.602176634e-19;

%% --- Kuyu tanimi ---
L  = 10e-9;         % hesap bolgesi [m]
N  = 1000;          % orgu noktasi
x  = linspace(-L/2, L/2, N)';
dx = x(2)-x(1);

% Sonlu derinlikte kare kuyu (istediginiz potansiyeli yazabilirsiniz)
V0 = 0.3*eV;        % kuyu derinligi
a  = 2e-9;          % kuyu genisligi
V  = V0*ones(N,1);
V(abs(x) < a/2) = 0;

%% --- Hamiltonyen (sonlu farklar) ---
% -hbar^2/(2m) d2/dx2 + V   ->  ucgen bantli matris
main = hbar^2/(me*dx^2) + V;
off  = -hbar^2/(2*me*dx^2)*ones(N-1,1);
H    = diag(main) + diag(off,1) + diag(off,-1);

[psi, E] = eig(H);
E = diag(E);
[E, idx] = sort(E);
psi = psi(:, idx);

%% --- Bagli durumlari yazdir ---
bound = find(E < V0);
fprintf('Bagli durum sayisi: %d\n', numel(bound));
for n = 1:min(5, numel(bound))
    fprintf('  E_%d = %.4f eV\n', n, E(n)/eV);
end

% Analitik sonsuz kuyu karsilastirmasi
fprintf('\nSonsuz kuyu (genislik %.1f nm) karsilastirmasi:\n', a*1e9);
for n = 1:3
    En_inf = n^2*pi^2*hbar^2/(2*me*a^2);
    fprintf('  n=%d: sayisal %.4f eV  |  sonsuz kuyu %.4f eV\n', ...
            n, E(n)/eV, En_inf/eV);
end

%% --- Grafik ---
figure('Color','w'); hold on; grid on;
plot(x*1e9, V/eV, 'k', 'LineWidth', 2, 'DisplayName','V(x)');
for n = 1:min(3, numel(bound))
    p = psi(:,n)/sqrt(trapz(x, psi(:,n).^2));   % normalize
    plot(x*1e9, E(n)/eV + 0.03*p/max(abs(p)), 'LineWidth', 1.5, ...
         'DisplayName', sprintf('n=%d, E=%.3f eV', n, E(n)/eV));
end
xlabel('x [nm]'); ylabel('Enerji [eV]');
title('Sonlu Kuantum Kuyusu: Bagli Durumlar');
legend('Location','best');
""",
    "V vektorunu degistirerek harmonik osilator, ucgen kuyu veya cift kuyu gibi "
    "her potansiyeli cozebilirsiniz — kodun geri kalani aynidir.",
    "Change the V vector to solve any potential — harmonic, triangular, double well — the rest of the code is unchanged.")

tpl("yorunge", "Gezegen yorungesi (simplektik Verlet)",
    "Planetary orbit (symplectic Verlet)",
    "yorunge|gezegen|kepler|orbit|planet|verlet|gok mekanigi|celestial",
    r"""clear; clc; close all;

%% --- Sabitler ---
G  = 6.67430e-11;
M  = 1.989e30;        % Gunes kutlesi [kg]
AU = 1.495978707e11;

%% --- Baslangic kosullari (Dunya benzeri) ---
r0 = [1*AU; 0];
v0 = [0; 29780];      % [m/s]

yil = 365.25*24*3600;
dt  = yil/2000;
Nt  = round(3*yil/dt);

r = r0; v = v0;
R = zeros(2, Nt); E = zeros(1, Nt);

acc = @(r) -G*M*r/norm(r)^3;

a = acc(r);
for n = 1:Nt
    % Velocity-Verlet: enerjiyi uzun vadede korur (ode45'in aksine)
    v_half = v + 0.5*dt*a;
    r      = r + dt*v_half;
    a      = acc(r);
    v      = v_half + 0.5*dt*a;

    R(:,n) = r;
    E(n)   = 0.5*norm(v)^2 - G*M/norm(r);   % birim kutle basina enerji
end

fprintf('Baslangic enerjisi : %.6e J/kg\n', E(1));
fprintf('Bitis enerjisi     : %.6e J/kg\n', E(end));
fprintf('Bagil enerji kaymasi: %.3e\n', abs((E(end)-E(1))/E(1)));

%% --- Grafikler ---
figure('Color','w');
subplot(1,2,1);
plot(R(1,:)/AU, R(2,:)/AU, 'LineWidth', 1.2); hold on; grid on;
plot(0, 0, 'yo', 'MarkerFaceColor','y', 'MarkerSize', 14);
xlabel('x [AU]'); ylabel('y [AU]'); title('Yorunge'); axis equal;

subplot(1,2,2);
plot((1:Nt)*dt/yil, (E-E(1))/abs(E(1)), 'LineWidth', 1.2); grid on;
xlabel('Zaman [yil]'); ylabel('\DeltaE/E_0');
title('Enerji Korunumu (simplektik)');
""",
    "Ayni problemi ode45 ile cozerseniz yorunge yavasca spirallesir. Simplektik "
    "integratorlerin uzun simulasyonlarda tercih edilme sebebi budur.",
    "Solving the same problem with ode45 makes the orbit slowly spiral. This is why symplectic integrators are preferred for long runs.")

tpl("egri_uydurma", "Veri analizi ve egri uydurma",
    "Data analysis and curve fitting",
    "egri uydurma|fit|regresyon|veri analizi|en kucuk kareler|curve fit|regression|least squares",
    r"""clear; clc; close all;

%% --- Veri (kendi olcumlerinizle degistirin) ---
x = (0:0.5:10)';
y_true = 3.2*exp(-0.4*x) + 1.1;
y = y_true + 0.08*randn(size(x));     % gurultu
sigma = 0.08*ones(size(y));           % olcum belirsizligi

%% --- 1) Dogrusal regresyon (polyfit) ---
[p, S] = polyfit(x, y, 1);
[yfit_lin, delta] = polyval(p, x, S);
fprintf('Dogrusal fit: y = %.4f x + %.4f\n', p(1), p(2));

%% --- 2) Dogrusal olmayan fit (fminsearch ile ki-kare minimizasyonu) ---
model = @(b, x) b(1)*exp(-b(2)*x) + b(3);
chi2  = @(b) sum(((y - model(b,x))./sigma).^2);
b0    = [1, 0.1, 0];
opts  = optimset('TolX',1e-10,'TolFun',1e-10,'MaxFunEvals',1e5);
[bhat, chi2min] = fminsearch(chi2, b0, opts);

dof = numel(y) - numel(bhat);
fprintf('\nUstel fit: y = %.4f*exp(-%.4f x) + %.4f\n', bhat(1), bhat(2), bhat(3));
fprintf('chi^2 = %.2f, serbestlik derecesi = %d, indirgenmis chi^2 = %.3f\n', ...
        chi2min, dof, chi2min/dof);
if abs(chi2min/dof - 1) < 0.5
    fprintf('-> Model veriyle uyumlu.\n');
else
    fprintf('-> Dikkat: model veya belirsizlik tahmini gozden gecirilmeli.\n');
end

%% --- Artiklar (residual) ---
res = y - model(bhat, x);

figure('Color','w');
subplot(2,1,1);
errorbar(x, y, sigma, 'o', 'MarkerFaceColor','b'); hold on; grid on;
xf = linspace(min(x), max(x), 300);
plot(xf, model(bhat, xf), 'r-', 'LineWidth', 2);
plot(xf, polyval(p, xf), 'g--', 'LineWidth', 1.2);
legend('Veri','Ustel fit','Dogrusal fit','Location','best');
ylabel('y'); title('Egri Uydurma');

subplot(2,1,2);
stem(x, res./sigma, 'filled'); grid on; hold on;
yline(0,'k-'); yline(1,'r--'); yline(-1,'r--');
xlabel('x'); ylabel('Artik / \sigma');
title('Normalize Artiklar (rastgele dagilmali)');
""",
    "Artik grafigi fit kalitesini gormenin en iyi yoludur: artiklarda desen "
    "varsa model yanlistir, R^2 yuksek olsa bile.",
    "The residual plot is the best diagnostic: any pattern in residuals means the model is wrong, however high R² is.")

tpl("monte_carlo", "Monte Carlo simulasyonu", "Monte Carlo simulation",
    "monte carlo|rastgele|olasilik|istatistik|random|sampling",
    r"""clear; clc; close all;

%% --- Ornek 1: pi sayisinin tahmini ---
N = 1e6;
p = rand(N,2);
inside = sum(sum(p.^2,2) <= 1);
pi_est = 4*inside/N;
err = abs(pi_est - pi);
fprintf('pi tahmini (N=%.0e): %.6f   hata: %.6f   beklenen ~%.6f\n', ...
        N, pi_est, err, 4/sqrt(N));

%% --- Ornek 2: Maxwell-Boltzmann hiz dagilimi ---
kB = 1.380649e-23;
T  = 300;                 % [K]
m  = 28*1.66053906892e-27; % azot molekulu [kg]

Np = 1e5;
% Her bilesen N(0, sqrt(kB*T/m)) dagilimindan gelir
sigma_v = sqrt(kB*T/m);
V = sigma_v*randn(Np,3);
speed = sqrt(sum(V.^2,2));

v_rms  = sqrt(mean(speed.^2));
v_mean = mean(speed);
v_mp   = sqrt(2*kB*T/m);

fprintf('\nMaxwell-Boltzmann (N2 @ %d K):\n', T);
fprintf('  En olasi hiz  : %.1f m/s (teori %.1f)\n', ...
        mode(round(speed/10)*10), v_mp);
fprintf('  Ortalama hiz  : %.1f m/s (teori %.1f)\n', ...
        v_mean, sqrt(8*kB*T/(pi*m)));
fprintf('  RMS hiz       : %.1f m/s (teori %.1f)\n', ...
        v_rms, sqrt(3*kB*T/m));

figure('Color','w');
histogram(speed, 100, 'Normalization','pdf', 'EdgeColor','none'); hold on; grid on;
vv = linspace(0, max(speed), 500);
f_theory = 4*pi*vv.^2 .* (m/(2*pi*kB*T))^(3/2) .* exp(-m*vv.^2/(2*kB*T));
plot(vv, f_theory, 'r-', 'LineWidth', 2);
xlabel('Hiz [m/s]'); ylabel('Olasilik yogunlugu');
title(sprintf('Maxwell-Boltzmann Hiz Dagilimi (T = %d K)', T));
legend('Monte Carlo','Analitik','Location','best');
""",
    "Monte Carlo hatasi N^(-1/2) ile azalir; duyarliligi 10 kat artirmak icin "
    "100 kat ornek gerekir. Buna karsilik hata boyuttan bagimsizdir.",
    "Monte Carlo error falls as N^(-1/2) — 100× the samples for 10× the precision — but is independent of dimension.")

tpl("rlc", "RLC devresi (gecici ve frekans yaniti)",
    "RLC circuit (transient and frequency response)",
    "rlc|devre|rezonans|empedans|circuit|resonance|impedance|bode",
    r"""clear; clc; close all;

%% --- Devre parametreleri ---
R = 10;        % [ohm]
L = 1e-3;      % [H]
C = 1e-6;      % [F]
V0 = 5;        % kaynak gerilimi [V]

w0   = 1/sqrt(L*C);
f0   = w0/(2*pi);
zeta = R/2*sqrt(C/L);
Q    = 1/(2*zeta);

fprintf('Rezonans frekansi : %.2f Hz\n', f0);
fprintf('Sonum orani zeta  : %.4f\n', zeta);
fprintf('Kalite faktoru Q  : %.2f\n', Q);
fprintf('Bant genisligi    : %.2f Hz\n', f0/Q);

%% --- Gecici cevap (seri RLC, basamak girisi) ---
% L*q'' + R*q' + q/C = V0  ->  y = [q; q']
f = @(t,y) [ y(2); (V0 - R*y(2) - y(1)/C)/L ];
tspan = [0 5e-3];
[t, y] = ode45(f, tspan, [0; 0], odeset('RelTol',1e-9));
Vc = y(:,1)/C;      % kondansator gerilimi
I  = y(:,2);        % akim

figure('Color','w');
subplot(2,1,1);
plot(t*1e3, Vc, 'LineWidth', 1.5); grid on; hold on;
yline(V0, 'r--');
xlabel('Zaman [ms]'); ylabel('V_C [V]'); title('Gecici Cevap');

subplot(2,1,2);
plot(t*1e3, I*1e3, 'LineWidth', 1.5); grid on;
xlabel('Zaman [ms]'); ylabel('Akim [mA]');

%% --- Frekans yaniti (Bode) ---
f_ax = logspace(2, 6, 1000);
w    = 2*pi*f_ax;
Z    = R + 1i*w*L + 1./(1i*w*C);
H    = (1./(1i*w*C))./Z;          % kondansator uzerindeki transfer fonksiyonu

figure('Color','w');
subplot(2,1,1);
semilogx(f_ax, 20*log10(abs(H)), 'LineWidth', 1.5); grid on; hold on;
xline(f0, 'r--', 'f_0');
ylabel('|H| [dB]'); title('Frekans Yaniti');

subplot(2,1,2);
semilogx(f_ax, rad2deg(angle(H)), 'LineWidth', 1.5); grid on; hold on;
xline(f0, 'r--');
xlabel('Frekans [Hz]'); ylabel('Faz [derece]');
""",
    "Q faktoru ne kadar yuksekse rezonans o kadar keskindir; radyo alicilarinda "
    "istasyon ayirt etme yetenegi dogrudan Q ile belirlenir.",
    "The higher the Q, the sharper the resonance; a radio's station selectivity is set directly by Q.")

tpl("dalga_denklemi", "Dalga denklemi (1B, sonlu farklar)",
    "Wave equation (1D, finite differences)",
    "dalga denklemi|duran dalga|string|wave equation|standing wave|tel",
    r"""clear; clc; close all;

%% --- Parametreler ---
L  = 1.0;        % tel uzunlugu [m]
c  = 100;        % dalga hizi [m/s]  (c = sqrt(T/mu))
Tson = 0.05;     % simulasyon suresi [s]

Nx = 201;
dx = L/(Nx-1);
x  = linspace(0, L, Nx)';

% CFL kararlilik kosulu: C = c*dt/dx <= 1
dt = 0.9*dx/c;
Nt = round(Tson/dt);
CFL = c*dt/dx;
fprintf('dt = %.3e s, CFL = %.3f (<=1 olmali)\n', dt, CFL);

%% --- Baslangic kosulu: ortada Gauss darbe, sifir hiz ---
u_prev = exp(-((x-0.5*L)/0.05).^2);
u_prev([1 end]) = 0;
u = u_prev;   % ilk adim (sifir baslangic hizi icin ozel formul)
u(2:end-1) = u_prev(2:end-1) + 0.5*CFL^2*(u_prev(3:end) - 2*u_prev(2:end-1) + u_prev(1:end-2));

figure('Color','w');
h = plot(x, u, 'LineWidth', 2); grid on;
axis([0 L -1.2 1.2]);
xlabel('x [m]'); ylabel('u(x,t)');
title('1B Dalga Denklemi - Sabit Uclar');

for n = 1:Nt
    u_new = zeros(Nx,1);
    u_new(2:end-1) = 2*u(2:end-1) - u_prev(2:end-1) + ...
                     CFL^2*(u(3:end) - 2*u(2:end-1) + u(1:end-2));
    u_new([1 end]) = 0;         % sabit uclar -> yansima ters isaretle olur
    u_prev = u;  u = u_new;

    if mod(n, 5) == 0
        set(h, 'YData', u);
        title(sprintf('t = %.4f s', n*dt));
        drawnow limitrate;
    end
end

%% --- Harmonikler ---
fprintf('\nSabit uclu telin harmonikleri:\n');
for n = 1:5
    fprintf('  n=%d: f = %.2f Hz, lambda = %.3f m\n', n, n*c/(2*L), 2*L/n);
end
""",
    "CFL > 1 olursa cozum patlar. Sabit uclarda darbe ters donerek yansir; "
    "serbest ucta (u_new(end)=u_new(end-1)) ayni isaretle yansir.",
    "If CFL > 1 the solution blows up. Fixed ends invert the reflected pulse; free ends preserve its sign.")

tpl("vektor_alan", "Elektrik/manyetik alan gorsellestirme",
    "Electric/magnetic field visualisation",
    "alan cizimi|vektor alan|elektrik alan|potansiyel|field plot|quiver|equipotential",
    r"""clear; clc; close all;

%% --- Sabitler ---
ke = 8.9875517862e9;

%% --- Yuk dagilimi: [x, y, q] ---
charges = [-0.3, 0,  1e-9;
            0.3, 0, -1e-9];      % elektrik dipol

%% --- Izgara ---
n = 40;
[X, Y] = meshgrid(linspace(-1, 1, n), linspace(-1, 1, n));
Ex = zeros(size(X)); Ey = zeros(size(X)); V = zeros(size(X));

for k = 1:size(charges,1)
    x0 = charges(k,1); y0 = charges(k,2); q = charges(k,3);
    dx = X - x0;  dy = Y - y0;
    r  = sqrt(dx.^2 + dy.^2);
    r(r < 0.05) = NaN;               % tekilligi maskele
    Ex = Ex + ke*q*dx./r.^3;
    Ey = Ey + ke*q*dy./r.^3;
    V  = V  + ke*q./r;
end

Emag = sqrt(Ex.^2 + Ey.^2);

figure('Color','w');
%% Esptansiyel egriler + alan cizgileri
contourf(X, Y, V, 40, 'LineStyle','none'); hold on;
colormap(jet); cb = colorbar; ylabel(cb, 'Potansiyel [V]');

% Alan vektorleri (normalize edilmis, yon gostermek icin)
q1 = quiver(X, Y, Ex./Emag, Ey./Emag, 0.5, 'k');
set(q1, 'LineWidth', 0.7);

for k = 1:size(charges,1)
    col = 'r'; if charges(k,3) < 0, col = 'b'; end
    plot(charges(k,1), charges(k,2), 'o', 'MarkerSize', 12, ...
         'MarkerFaceColor', col, 'MarkerEdgeColor','k');
end

xlabel('x [m]'); ylabel('y [m]');
title('Elektrik Dipol: Alan Cizgileri ve Esptansiyel Egriler');
axis equal tight;
""",
    "charges matrisine satir ekleyerek istediginiz yuk dagilimini kurabilirsiniz. "
    "Alan cizgileri her zaman esptansiyel egrilere diktir — grafikte bunu dogrulayin.",
    "Add rows to the charges matrix for any configuration. Field lines are always perpendicular to equipotentials — verify it in the plot.")


# ---------------------------------------------------------------------------
# Sablonlar Turkce yorumlarla yazildi. Ingilizce konusurken ayni kodu ikinci
# kez yazmak yerine yorum/etiket metinlerini cevirtiyoruz; boylece tek bir
# kaynak dosya bakimda kaliyor ve kodun kendisi hicbir zaman degismiyor.
_TR_EN = {
    # bolum basliklari
    "Parametreler": "Parameters",
    "Fiziksel parametreler": "Physical parameters",
    "Devre parametreleri": "Circuit parameters",
    "Sabitler (SI)": "Constants (SI)",
    "Sabitler": "Constants",
    "Analitik cozum": "Analytic solution",
    "Sayisal cozum": "Numerical solution",
    "Grafikler": "Plots",
    "Grafik": "Plot",
    "Ayriklastirma": "Discretisation",
    "Baslangic ve sinir kosullari": "Initial and boundary conditions",
    "Baslangic kosullari (Dunya benzeri)": "Initial conditions (Earth-like)",
    "Baslangic kosulu: ortada Gauss darbe, sifir hiz":
        "Initial condition: Gaussian pulse at centre, zero velocity",
    "Kuyu tanimi": "Well definition",
    "Hamiltonyen (sonlu farklar)": "Hamiltonian (finite differences)",
    "Bagli durumlari yazdir": "Print bound states",
    "Baskin frekanslari bul": "Find dominant frequencies",
    "Frekans yaniti (Bode)": "Frequency response (Bode)",
    "Gecici cevap (seri RLC, basamak girisi)":
        "Transient response (series RLC, step input)",
    "Sentetik sinyal (kendi verinizle degistirin)":
        "Synthetic signal (replace with your own data)",
    "Veri (kendi olcumlerinizle degistirin)":
        "Data (replace with your own measurements)",
    "Yuk dagilimi: [x, y, q]": "Charge distribution: [x, y, q]",
    "Izgara": "Grid",
    "Harmonikler": "Harmonics",
    "Artiklar (residual)": "Residuals",
    "1) Dogrusal regresyon (polyfit)": "1) Linear regression (polyfit)",
    "2) Dogrusal olmayan fit (fminsearch ile ki-kare minimizasyonu)":
        "2) Nonlinear fit (chi-square minimisation via fminsearch)",
    "Ornek 1: pi sayisinin tahmini": "Example 1: estimating pi",
    "Ornek 2: Maxwell-Boltzmann hiz dagilimi":
        "Example 2: Maxwell-Boltzmann speed distribution",
    # degisken aciklamalari
    "ilk hiz [m/s]": "initial speed [m/s]",
    "ilk konum [m]": "initial position [m]",
    "atis acisi [derece]": "launch angle [degrees]",
    "baslangic yuksekligi [m]": "initial height [m]",
    "yercekimi ivmesi [m/s^2]": "gravitational acceleration [m/s^2]",
    "kutle [kg]": "mass [kg]",
    "yay sabiti [N/m]": "spring constant [N/m]",
    "sonum katsayisi [N.s/m]": "damping coefficient [N.s/m]",
    "ip uzunlugu [m]": "pendulum length [m]",
    "karsilastirilacak baslangic acilari": "initial angles to compare",
    "ornekleme frekansi [Hz]": "sampling frequency [Hz]",
    "sure [s]": "duration [s]",
    "gurultu": "noise",
    "olcum belirsizligi": "measurement uncertainty",
    "cubuk uzunlugu [m]": "rod length [m]",
    "isil yayinim [m^2/s]": "thermal diffusivity [m^2/s]",
    "simulasyon suresi [s]": "simulation time [s]",
    "orgu noktasi": "grid points",
    "ortada sicak bolge": "hot region in the middle",
    "uclar sabit 0 C (Dirichlet)": "ends held at 0 C (Dirichlet)",
    "hesap bolgesi [m]": "computational domain [m]",
    "kuyu derinligi": "well depth",
    "kuyu genisligi": "well width",
    "Gunes kutlesi [kg]": "solar mass [kg]",
    "kaynak gerilimi [V]": "source voltage [V]",
    "tel uzunlugu [m]": "string length [m]",
    "dalga hizi [m/s]  (c = sqrt(T/mu))": "wave speed [m/s]  (c = sqrt(T/mu))",
    "azot molekulu [kg]": "nitrogen molecule [kg]",
    "elektrik dipol": "electric dipole",
    # satir ici aciklamalar
    "dogal acisal frekans": "natural angular frequency",
    "sonum orani": "damping ratio",
    "toplam mekanik enerji": "total mechanical energy",
    "birim kutle basina enerji": "energy per unit mass",
    "kucuk aci yaklasimindaki periyot": "period in the small-angle approximation",
    "TAM denklem (sin, theta degil)": "FULL equation (sin, not theta)",
    "Gercek periyodu sifir gecislerinden olc":
        "Measure the true period from zero crossings",
    "iki tarafli genlik spektrumu": "two-sided amplitude spectrum",
    "tek tarafli": "one-sided",
    "menzil": "range",
    "maksimum yukseklik": "maximum height",
    "ikinci derece denklem": "quadratic equation",
    "Ucus suresi": "Flight time",
    "Menzil": "Range",
    "Maks. yuks.": "Max height",
    "KARARLILIK KOSULU (acik yontem icin zorunlu):  r = alpha*dt/dx^2 <= 0.5":
        "STABILITY CONDITION (required for the explicit scheme): r = alpha*dt/dx^2 <= 0.5",
    "CFL kararlilik kosulu: C = c*dt/dx <= 1":
        "CFL stability condition: C = c*dt/dx <= 1",
    "ilk adim (sifir baslangic hizi icin ozel formul)":
        "first step (special formula for zero initial velocity)",
    "sabit uclar -> yansima ters isaretle olur":
        "fixed ends -> reflection inverts the pulse",
    "Sonlu derinlikte kare kuyu (istediginiz potansiyeli yazabilirsiniz)":
        "Finite square well (write any potential you like here)",
    "ucgen bantli matris": "tridiagonal matrix",
    "Analitik sonsuz kuyu karsilastirmasi": "Comparison with the infinite well",
    "kondansator gerilimi": "capacitor voltage",
    "kondansator uzerindeki transfer fonksiyonu":
        "transfer function across the capacitor",
    "tekilligi maskele": "mask the singularity",
    "Alan vektorleri (normalize edilmis, yon gostermek icin)":
        "Field vectors (normalised, to show direction)",
    "Esptansiyel egriler + alan cizgileri": "Equipotentials + field lines",
    "Her bilesen N(0, sqrt(kB*T/m)) dagilimindan gelir":
        "Each component is drawn from N(0, sqrt(kB*T/m))",
    "akim": "current",
    "normalize": "normalise",
    # fprintf / etiket metinleri
    "Dogal frekans w0": "Natural frequency w0",
    "Sonum orani zeta": "Damping ratio zeta",
    "az sonumlu": "underdamped",
    "kritik sonumlu": "critically damped",
    "asiri sonumlu": "overdamped",
    "Kucuk aci periyodu": "Small-angle period",
    "sapma": "deviation",
    "En guclu 3 bilesen:": "Three strongest components:",
    "genlik": "amplitude",
    "kararlilik icin <= 0.5 olmali": "must be <= 0.5 for stability",
    "<=1 olmali": "must be <= 1",
    "Bagli durum sayisi": "Number of bound states",
    "Sonsuz kuyu (genislik": "Infinite well (width",
    "karsilastirmasi": "comparison",
    "sayisal": "numerical",
    "sonsuz kuyu": "infinite well",
    "Baslangic enerjisi": "Initial energy",
    "Bitis enerjisi": "Final energy",
    "Bagil enerji kaymasi": "Relative energy drift",
    "Dogrusal fit": "Linear fit",
    "Ustel fit": "Exponential fit",
    "serbestlik derecesi": "degrees of freedom",
    "indirgenmis": "reduced",
    "Model veriyle uyumlu.": "Model is consistent with the data.",
    "Dikkat: model veya belirsizlik tahmini gozden gecirilmeli.":
        "Warning: revisit the model or the uncertainty estimate.",
    "pi tahmini": "pi estimate",
    "hata": "error",
    "beklenen": "expected",
    "En olasi hiz": "Most probable speed",
    "Ortalama hiz": "Mean speed",
    "RMS hiz": "RMS speed",
    "teori": "theory",
    "Rezonans frekansi": "Resonance frequency",
    "Kalite faktoru Q": "Quality factor Q",
    "Bant genisligi": "Bandwidth",
    "Sabit uclu telin harmonikleri:": "Harmonics of a fixed-end string:",
    # grafik etiketleri
    "Yatay mesafe x [m]": "Horizontal distance x [m]",
    "Yukseklik y [m]": "Height y [m]",
    "Egik Atis": "Projectile Motion",
    "Yorunge": "Trajectory",
    "Carpma noktasi": "Impact point",
    "Tepe noktasi": "Apex",
    "Zaman [s]": "Time [s]",
    "Zaman [ms]": "Time [ms]",
    "Zaman [yil]": "Time [years]",
    "Konum [m]": "Position [m]",
    "Konum x [m]": "Position x [m]",
    "Hiz [m/s]": "Velocity [m/s]",
    "Enerji [J]": "Energy [J]",
    "Enerji [eV]": "Energy [eV]",
    "Aci [derece]": "Angle [degrees]",
    "Faz [derece]": "Phase [degrees]",
    "Akim [mA]": "Current [mA]",
    "Frekans [Hz]": "Frequency [Hz]",
    "Genlik": "Amplitude",
    "Sicaklik": "Temperature",
    "Olasilik yogunlugu": "Probability density",
    "Potansiyel [V]": "Potential [V]",
    "Sonumlu Harmonik Osilator": "Damped Harmonic Oscillator",
    "Faz Uzayi": "Phase Space",
    "Zaman Alani": "Time Domain",
    "Tek Tarafli Genlik Spektrumu": "One-Sided Amplitude Spectrum",
    "Sarkac: Genlik Periyodu Nasil Etkiler":
        "Pendulum: How Amplitude Affects the Period",
    "1B Isi Denklemi - Acik Sonlu Farklar":
        "1D Heat Equation - Explicit Finite Differences",
    "1B Dalga Denklemi - Sabit Uclar": "1D Wave Equation - Fixed Ends",
    "Sonlu Kuantum Kuyusu: Bagli Durumlar":
        "Finite Quantum Well: Bound States",
    "Enerji Korunumu (simplektik)": "Energy Conservation (symplectic)",
    "Egri Uydurma": "Curve Fitting",
    "Normalize Artiklar (rastgele dagilmali)":
        "Normalised Residuals (should look random)",
    "Artik": "Residual",
    "Maxwell-Boltzmann Hiz Dagilimi": "Maxwell-Boltzmann Speed Distribution",
    "Gecici Cevap": "Transient Response",
    "Frekans Yaniti": "Frequency Response",
    "Elektrik Dipol: Alan Cizgileri ve Esptansiyel Egriler":
        "Electric Dipole: Field Lines and Equipotentials",
    "Veri": "Data",
    "Analitik": "Analytic",
    "Zarf": "Envelope",
    "ParguszPhysics tarafindan uretildi": "Generated by ParguszPhysics",
}

# Uzun ifadeler once degistirilmeli, aksi halde kisa parcalar uzunlari bozar
_TR_EN_ORDERED = sorted(_TR_EN.items(), key=lambda kv: -len(kv[0]))


def localize(code, lang):
    """Sablon yorumlarini/etiketlerini hedef dile cevir. Kod degismez."""
    if lang != "en":
        return code
    out = code
    for tr, en in _TR_EN_ORDERED:
        out = out.replace(tr, en)
    return out


tpl("sembolik", "Sembolik hesap (Symbolic Toolbox)", "Symbolic computation",
    "sembolik|symbolic|syms|turev integral sembolik|analitik cozum|cebirsel",
    r"""clear; clc;

%% --- Sembolik degiskenler ---
syms x y t m k w0 zeta positive
syms C1 C2

%% --- Turev ve integral ---
f = x^2*sin(x);
fprintf('f(x)      = %s\n', char(f));
fprintf('df/dx     = %s\n', char(diff(f, x)));
fprintf('∫f dx     = %s\n', char(int(f, x)));
fprintf('∫f dx 0-π = %s\n', char(int(f, x, 0, pi)));

%% --- Limit ve seri ---
fprintf('lim sin(x)/x, x->0 = %s\n', char(limit(sin(x)/x, x, 0)));
fprintf('Taylor exp(x), 5 terim = %s\n', char(taylor(exp(x), x, 'Order', 5)));

%% --- Denklem cozme ---
coz = solve(x^2 - 5*x + 6 == 0, x);
fprintf('x^2-5x+6=0 -> x = %s\n', char(coz.'));

%% --- Diferansiyel denklem (sonumlu osilator) ---
syms u(t)
ode = diff(u,t,2) + 2*zeta*w0*diff(u,t) + w0^2*u == 0;
cozum = dsolve(ode, [u(0)==1, subs(diff(u,t),t,0)==0]);
fprintf('\nSonumlu osilator cozumu:\n  u(t) = %s\n', char(simplify(cozum)));

%% --- Sembolikten sayisala ---
w0_deg = 10; zeta_deg = 0.1;
u_say = matlabFunction(subs(cozum, [w0 zeta], [w0_deg zeta_deg]));
tt = linspace(0, 5, 500);
figure('Color','w');
plot(tt, u_say(tt), 'LineWidth', 1.6); grid on;
xlabel('Zaman [s]'); ylabel('u(t)');
title('Sembolik cozumun sayisal degerlendirmesi');
""",
    "Symbolic Toolbox yoksa bu kod calismaz. Octave'da `pkg load symbolic` "
    "ile benzer islevler kullanilabilir.",
    "Requires the Symbolic Toolbox. In Octave use `pkg load symbolic`.")

tpl("optimizasyon", "Optimizasyon ve kok bulma", "Optimisation and root finding",
    "optimizasyon|minimize|maksimum bul|kok bulma|fzero|fminsearch|en iyi",
    r"""clear; clc; close all;

%% --- 1) Kok bulma ---
f = @(x) x.^3 - 2*x - 5;
kok = fzero(f, 2);
fprintf('f(x)=x^3-2x-5 kokleri: x = %.10f\n', kok);
fprintf('  dogrulama: f(x) = %.3e (sifira yakin olmali)\n', f(kok));

%% --- 2) Tek degiskenli minimum ---
g = @(x) (x-3).^2 + 2;
[xmin, fmin] = fminbnd(g, -10, 10);
fprintf('\ng(x)=(x-3)^2+2 minimumu: x=%.6f, g=%.6f\n', xmin, fmin);

%% --- 3) Cok degiskenli minimum (Rosenbrock) ---
ros = @(v) (1-v(1))^2 + 100*(v(2)-v(1)^2)^2;
opts = optimset('TolX',1e-10,'TolFun',1e-10,'MaxFunEvals',1e5);
[vmin, fval] = fminsearch(ros, [-1.2, 1], opts);
fprintf('\nRosenbrock minimumu: (%.6f, %.6f), f=%.3e\n', vmin(1), vmin(2), fval);
fprintf('  gercek minimum (1,1) olmali\n');

%% --- 4) Fiziksel ornek: en iyi atis acisi ---
v0 = 25; g_ac = 9.81; h0 = 2;      % 2 m yukseklikten atis
menzil = @(th) -(v0*cos(th)/g_ac) * (v0*sin(th) + sqrt((v0*sin(th))^2 + 2*g_ac*h0));
[th_opt, R_neg] = fminbnd(menzil, 0, pi/2);
fprintf('\n%.1f m yukseklikten %.0f m/s ile atis:\n', h0, v0);
fprintf('  en iyi aci = %.2f derece (duz zeminde 45 olurdu)\n', rad2deg(th_opt));
fprintf('  menzil     = %.2f m\n', -R_neg);

th = linspace(0.01, pi/2-0.01, 300);
figure('Color','w');
plot(rad2deg(th), -arrayfun(menzil, th), 'LineWidth', 1.8); hold on; grid on;
plot(rad2deg(th_opt), -R_neg, 'ro', 'MarkerFaceColor','r');
xlabel('Atis acisi [derece]'); ylabel('Menzil [m]');
title('Yukseklikten atista en iyi aci 45 dereceden kucuktur');
""",
    "Baslangic yuksekligi varken en iyi aci 45 dereceden kucuktur; kod bunu "
    "sayisal olarak gosterir.",
    "With a launch height the optimal angle is below 45 degrees; the code shows this numerically.")

tpl("laplace_pde", "Laplace denklemi (2B potansiyel)",
    "Laplace equation (2D potential)",
    "laplace|potansiyel dagilimi|2b pde|sinir deger|elektrostatik alan cozumu",
    r"""clear; clc; close all;

%% --- Izgara ---
N = 60;                       % kenar basina nokta
V = zeros(N, N);

%% --- Sinir kosullari (Dirichlet) ---
V(1, :)   = 100;              % ust kenar 100 V
V(end, :) = 0;                % alt kenar 0 V
V(:, 1)   = 0;                % sol kenar
V(:, end) = 0;                % sag kenar

%% --- Gauss-Seidel ile cozum ---
tol = 1e-5; hata = inf; adim = 0;
while hata > tol && adim < 20000
    Vesk = V;
    for i = 2:N-1
        for j = 2:N-1
            V(i,j) = 0.25*(V(i+1,j) + V(i-1,j) + V(i,j+1) + V(i,j-1));
        end
    end
    hata = max(max(abs(V - Vesk)));
    adim = adim + 1;
end
fprintf('Yakinsama: %d adim, son hata %.2e\n', adim, hata);

%% --- Elektrik alan (potansiyelin gradyani) ---
[Ex, Ey] = gradient(-V);

figure('Color','w');
contourf(V, 30, 'LineStyle','none'); hold on;
colormap(jet); cb = colorbar; ylabel(cb, 'Potansiyel [V]');
adim_ok = 4;
quiver(1:adim_ok:N, 1:adim_ok:N, Ex(1:adim_ok:N,1:adim_ok:N), ...
       Ey(1:adim_ok:N,1:adim_ok:N), 'k');
title('Laplace denklemi: potansiyel ve elektrik alan');
xlabel('x'); ylabel('y'); axis equal tight;
""",
    "Gauss-Seidel basit ama yavastir; buyuk izgaralarda `A\\b` ile dogrudan "
    "cozum ya da cok izgara (multigrid) yontemi tercih edilir.",
    "Gauss-Seidel is simple but slow; for large grids use a direct solve or multigrid.")

tpl("hareket_denklemi", "N-cisim problemi (yercekimi)", "N-body gravitational problem",
    "n cisim|coklu cisim|yercekimi simulasyonu|gunes sistemi|kaotik yorunge",
    r"""clear; clc; close all;

%% --- Sabitler ve baslangic ---
G = 6.67430e-11;
AU = 1.495978707e11;
yil = 365.25*24*3600;

% [kutle(kg), x, y (m), vx, vy (m/s)]
cisimler = [
    1.989e30,      0,        0,        0,       0;        % Gunes
    5.972e24,      1*AU,     0,        0,       29780;    % Dunya
    6.417e23,      1.524*AU, 0,        0,       24070;    % Mars
];
N = size(cisimler, 1);
m = cisimler(:,1);
r = cisimler(:,2:3);
v = cisimler(:,4:5);

dt = yil/2000;
Nt = round(2*yil/dt);
iz = zeros(Nt, N, 2);

    function a = ivme(r, m, G)
        N = size(r,1); a = zeros(N,2);
        for i = 1:N
            for j = 1:N
                if i == j, continue; end
                d = r(j,:) - r(i,:);
                a(i,:) = a(i,:) + G*m(j)*d/norm(d)^3;
            end
        end
    end

a = ivme(r, m, G);
for n = 1:Nt
    % Velocity-Verlet: enerjiyi uzun vadede korur
    v_yari = v + 0.5*dt*a;
    r = r + dt*v_yari;
    a = ivme(r, m, G);
    v = v_yari + 0.5*dt*a;
    iz(n,:,:) = r;
end

figure('Color','w'); hold on; grid on;
renk = {'y','b','r'};
ad = {'Gunes','Dunya','Mars'};
for i = 1:N
    plot(squeeze(iz(:,i,1))/AU, squeeze(iz(:,i,2))/AU, renk{i}, ...
         'LineWidth', 1.3, 'DisplayName', ad{i});
end
plot(0,0,'yo','MarkerFaceColor','y','MarkerSize',12,'HandleVisibility','off');
xlabel('x [AU]'); ylabel('y [AU]'); axis equal;
title('Uc cisim: Gunes-Dunya-Mars'); legend('Location','best');
""",
    "Cisim sayisi arttikca maliyet N^2 ile buyur. Cok sayida cisimde "
    "Barnes-Hut agac yontemi kullanilir.",
    "Cost grows as N^2; for many bodies use the Barnes-Hut tree method.")

tpl("istatistik_hata", "Olcum verisi ve hata yayilimi",
    "Measurement data and error propagation",
    "hata yayilimi|belirsizlik hesabi|olcum analizi|standart sapma|deney verisi",
    r"""clear; clc; close all;

%% --- Sarkacla g olcumu (ornek deney verisi) ---
L  = 1.000;  dL = 0.002;        % ip uzunlugu ve belirsizligi [m]
% 10 salinim suresi, 8 tekrar [s]
T10 = [20.05 19.98 20.11 20.02 19.95 20.08 20.01 20.06];

T   = mean(T10)/10;                     % tek salinim periyodu
sT  = std(T10)/10;                      % standart sapma
dT  = sT/sqrt(numel(T10));              % ortalamanin standart hatasi

g   = 4*pi^2*L/T^2;
% Hata yayilimi: dg/g = sqrt((dL/L)^2 + (2 dT/T)^2)
dg  = g*sqrt((dL/L)^2 + (2*dT/T)^2);

fprintf('Periyot  T = %.4f ± %.4f s\n', T, dT);
fprintf('Uzunluk  L = %.3f ± %.3f m\n', L, dL);
fprintf('SONUC    g = %.3f ± %.3f m/s^2\n', g, dg);
fprintf('Gercek deger 9.807 -> sapma %.2f sigma\n', abs(g-9.807)/dg);

%% Hangi terim baskin?
kL = (dL/L)^2; kT = (2*dT/T)^2;
fprintf('\nBelirsizlige katki: L %%%.1f, T %%%.1f\n', ...
        100*kL/(kL+kT), 100*kT/(kL+kT));
fprintf('-> Periyot hatasi 2 kat agirlikli girer; once onu iyilestirin.\n');

figure('Color','w');
subplot(1,2,1);
histogram(T10/10, 6, 'FaceColor',[.3 .5 .9]); grid on;
xlabel('Periyot [s]'); ylabel('Sayim'); title('Olcum dagilimi');
subplot(1,2,2);
errorbar(1, g, dg, 'o', 'MarkerFaceColor','b', 'LineWidth',1.5); hold on;
yline(9.807, 'r--', 'gercek deger'); grid on;
xlim([0.5 1.5]); ylabel('g [m/s^2]'); title('Sonuc ve belirsizligi');
""",
    "Periyot hatasi formulde kare olarak gectigi icin belirsizlige 2 kat "
    "agirlikla girer; kod bunu sayisal olarak gosterir.",
    "The period error enters squared, so it carries double weight; the code shows this.")


def search_template(query):
    q = query.lower()
    for a, b in {"ı": "i", "ş": "s", "ğ": "g", "ü": "u", "ö": "o", "ç": "c"}.items():
        q = q.replace(a, b)
    best, best_score = None, 0
    for key, t in TEMPLATES.items():
        score = 0
        for kw in t["kw"]:
            if kw and kw in q:
                score += 10 + len(kw)
        if score > best_score:
            best, best_score = (key, t), score
    return best


def generic_from_expression(expr_text, var="x", lang="tr"):
    """Herhangi bir matematiksel ifade icin MATLAB kodu uret."""
    try:
        code = solver.to_matlab(expr_text)
    except Exception:
        code = expr_text
    title = "Ifade degerlendirme ve cizim" if lang == "tr" else "Expression evaluation and plot"
    return _hdr(title, title, lang) + """clear; clc; close all;

%%%% --- Ifade: %s ---
%s = linspace(-10, 10, 1000);
y = %s;

figure('Color','w');
plot(%s, y, 'LineWidth', 1.8); grid on;
xlabel('%s'); ylabel('y');
title('y = %s');

fprintf('En kucuk deger: %%.6g  (%s = %%.4g)\\n', min(y), %s(find(y==min(y),1)));
fprintf('En buyuk deger: %%.6g  (%s = %%.4g)\\n', max(y), %s(find(y==max(y),1)));
""" % (expr_text, var, code.replace("*", ".*").replace("/", "./").replace("^", ".^"),
       var, var, expr_text, var, var, var, var)


def from_formula(f, lang="tr"):
    """Formul veritabanindaki bir formul icin MATLAB fonksiyonu uret."""
    name = f["id"]
    syms = list(f["vars"].keys())
    title = f["tr"] if lang == "tr" else f["en"]
    lines = [_hdr(title, title, lang)]
    lines.append("%% Formul: %s\n" % f["eq"])
    lines.append("clear; clc;\n")
    lines.append("%% --- Degiskenler ---")
    for s in syms:
        t, e, u = f["vars"][s]
        label = t if lang == "tr" else e
        lines.append("%-8s = 1.0;   %% %s%s" % (s, label, (" [%s]" % u) if u else ""))
    lines.append("")
    eq = f["eq"]
    if "=" in eq:
        lhs, rhs = eq.split("=", 1)
        lhs, rhs = lhs.strip(), rhs.strip()
    else:
        lhs, rhs = "sonuc", eq
    m_rhs = rhs
    for op_from, op_to in (("**", "^"),):
        m_rhs = m_rhs.replace(op_from, op_to)
    m_rhs = m_rhs.replace("*", ".*").replace("/", "./").replace("^", ".^")
    lines.append("%%%% --- Hesap ---")
    lines.append("%s = %s;" % (lhs, m_rhs))
    lines.append("")
    lines.append("fprintf('%s = %%.6g\\n', %s);" % (lhs, lhs))
    return localize("\n".join(lines), lang)


# ── Ek sablonlar (lineer cebir, kontrol, sayisal yontemler, gorsellestirme) ──

tpl("matris_lineer", "Lineer denklem sistemi ve ozdegerler",
    "Linear systems and eigenvalues",
    "matris|lineer denklem|denklem sistemi|ozdeger|ozvektor|determinant|"
    "ters matris|matrix|linear system|eigenvalue|eigenvector|inverse",
    r"""clear; clc;

%% --- Lineer denklem sistemi: A*x = b ---
A = [ 4 -2  1;
     -2  4 -2;
      1 -2  4];
b = [11; -16; 17];

x = A\b;                 % MATLAB'de dogru yol: ters alma degil sol bolme
fprintf('Cozum x:\n'); disp(x);
fprintf('Kalinti ||A*x-b|| = %.3e\n', norm(A*x - b));

%% --- Kosul sayisi: sistem ne kadar guvenilir? ---
fprintf('Kosul sayisi = %.4g\n', cond(A));
if cond(A) > 1e10
    warning('Sistem kotu kosullu, sonuca guvenme.');
end

%% --- Ozdeger ve ozvektorler ---
[V, D] = eig(A);
lambda = diag(D);
fprintf('\nOzdegerler:\n'); disp(lambda.');

% Dogrulama: A*v = lambda*v
for k = 1:numel(lambda)
    hata = norm(A*V(:,k) - lambda(k)*V(:,k));
    fprintf('  ozdeger %d: %8.4f   dogrulama hatasi %.2e\n', k, lambda(k), hata);
end

%% --- Fiziksel yorum: kuplajli kutle-yay sisteminin modlari ---
% A bir sertlik matrisi ise ozdegerler mod frekanslarinin karesidir.
w = sqrt(abs(lambda));
fprintf('\nMod frekanslari [rad/s]: '); fprintf('%.4f  ', w); fprintf('\n');

figure('Color','w');
bar(V); grid on;
xlabel('Serbestlik derecesi'); ylabel('Genlik');
title('Normal modlar (ozvektorler)');
legend(arrayfun(@(k) sprintf('Mod %d', k), 1:numel(lambda), ...
       'UniformOutput', false), 'Location','best');
""",
    "A\\b kullan, inv(A)*b kullanma: daha hizli ve sayisal olarak daha kararli.",
    "Use A\\b instead of inv(A)*b: faster and numerically more stable.")


tpl("ode_sistem", "Genel diferansiyel denklem sistemi (durum uzayi)",
    "General ODE system (state space)",
    "diferansiyel denklem|ode45|durum uzayi|denklem sistemi coz|"
    "baslangic deger|ode|state space|initial value problem|solve ode",
    r"""clear; clc; close all;

%% Ornek: Lorenz sistemi — kaotik davranisin klasik ornegi
% dx/dt = sigma*(y - x)
% dy/dt = x*(rho - z) - y
% dz/dt = x*y - beta*z

sigma = 10;  rho = 28;  beta = 8/3;

f = @(t, u) [ sigma*(u(2) - u(1));
              u(1)*(rho - u(3)) - u(2);
              u(1)*u(2) - beta*u(3) ];

u0    = [1; 1; 1];          % baslangic durumu
tspan = [0 50];

% RelTol/AbsTol: kaotik sistemlerde varsayilan tolerans yetmez
opts = odeset('RelTol', 1e-9, 'AbsTol', 1e-11);
[t, u] = ode45(f, tspan, u0, opts);

fprintf('Adim sayisi: %d\n', numel(t));
fprintf('Son durum  : [%.4f %.4f %.4f]\n', u(end,1), u(end,2), u(end,3));

figure('Color','w');
subplot(1,2,1);
plot3(u(:,1), u(:,2), u(:,3), 'LineWidth', 0.7); grid on;
xlabel('x'); ylabel('y'); zlabel('z'); title('Faz uzayi yorungesi'); view(30,20);

subplot(1,2,2);
plot(t, u(:,1), 'LineWidth', 1); grid on;
xlabel('t [s]'); ylabel('x(t)'); title('Zaman serisi');

%% --- Baslangic kosuluna duyarlilik ---
[t2, u2] = ode45(f, tspan, u0 + [1e-8; 0; 0], opts);
ortak = min(numel(t), numel(t2));
figure('Color','w');
semilogy(t(1:ortak), abs(u(1:ortak,1) - u2(1:ortak,1)) + eps, 'LineWidth', 1);
grid on; xlabel('t [s]'); ylabel('|fark|');
title('Baslangicta 10^{-8} fark nasil buyuyor');
""",
    "ode45 degisken adimlidir; katı (stiff) sistemlerde ode15s kullan.",
    "ode45 is adaptive; use ode15s for stiff systems.")


tpl("kontrol_sistem", "Transfer fonksiyonu ve sistem yaniti",
    "Transfer function and system response",
    "transfer fonksiyonu|basamak yaniti|step response|kontrol|bode|"
    "geri besleme|kararlilik|control system|feedback|stability|pid",
    r"""clear; clc; close all;

%% Ikinci mertebe sistem: G(s) = wn^2 / (s^2 + 2*zeta*wn*s + wn^2)
wn   = 5;        % dogal frekans [rad/s]
zeta = 0.3;      % sonum orani

num = wn^2;
den = [1, 2*zeta*wn, wn^2];

%% --- Kutuplar ve kararlilik ---
p = roots(den);
fprintf('Kutuplar:\n'); disp(p);
if all(real(p) < 0)
    fprintf('Sistem KARARLI (tum kutuplar sol yari duzlemde).\n');
else
    fprintf('Sistem KARARSIZ.\n');
end

%% --- Basamak yaniti (Control Toolbox olmadan) ---
t  = linspace(0, 5, 1000);
wd = wn*sqrt(1 - zeta^2);                       % sonumlu frekans
y  = 1 - exp(-zeta*wn*t).*(cos(wd*t) + (zeta*wn/wd)*sin(wd*t));

Mp = exp(-pi*zeta/sqrt(1-zeta^2))*100;          % asim yuzdesi
ts = 4/(zeta*wn);                                % %2 yerlesme suresi
fprintf('Asim      : %%%.2f\n', Mp);
fprintf('Yerlesme  : %.3f s\n', ts);

figure('Color','w');
subplot(2,1,1);
plot(t, y, 'LineWidth', 1.6); hold on; grid on;
yline(1, 'k--'); yline(1.02, 'r:'); yline(0.98, 'r:');
xlabel('t [s]'); ylabel('y(t)'); title('Basamak yaniti');

%% --- Frekans yaniti (Bode) ---
w   = logspace(-1, 2, 500);
s   = 1i*w;
G   = num ./ (s.^2 + 2*zeta*wn*s + wn^2);
mag = 20*log10(abs(G));
faz = angle(G)*180/pi;

subplot(2,1,2);
semilogx(w, mag, 'LineWidth', 1.4); grid on;
xlabel('\omega [rad/s]'); ylabel('|G| [dB]'); title('Bode genlik egrisi');
""",
    "zeta<1 sonumlu salinim, zeta=1 kritik sonum, zeta>1 asiri sonum demektir.",
    "zeta<1 underdamped, zeta=1 critically damped, zeta>1 overdamped.")


tpl("sayisal_integral", "Sayisal turev, integral ve interpolasyon",
    "Numerical derivative, integral and interpolation",
    "sayisal integral|sayisal turev|trapz|integral hesapla|"
    "interpolasyon|ara deger|numerical integration|derivative|interp",
    r"""clear; clc; close all;

%% --- Fonksiyon ve analitik karsiligi (dogrulama icin) ---
f      = @(x) exp(-x.^2).*sin(3*x);
f_int  = @(a,b) integral(f, a, b);      % yuksek dogruluklu referans

a = 0; b = 3;

%% --- Farkli integral yontemleri karsilastirmasi ---
for N = [11, 51, 201, 1001]
    x  = linspace(a, b, N);
    y  = f(x);
    I_trapz  = trapz(x, y);
    I_simp   = simpson(x, y);
    I_ref    = f_int(a, b);
    fprintf('N=%4d  trapz hata=%.3e   simpson hata=%.3e\n', ...
            N, abs(I_trapz-I_ref), abs(I_simp-I_ref));
end
fprintf('Referans integral = %.10f\n', f_int(a,b));

%% --- Sayisal turev ve analitik turevle karsilastirma ---
x  = linspace(a, b, 400);
h  = x(2) - x(1);
dy_merkezi = (f(x+h) - f(x-h)) / (2*h);        % O(h^2) merkezi fark
dy_ileri   = (f(x+h) - f(x)) / h;              % O(h) ileri fark
dy_gercek  = -2*x.*exp(-x.^2).*sin(3*x) + 3*exp(-x.^2).*cos(3*x);

figure('Color','w');
subplot(2,1,1);
plot(x, f(x), 'LineWidth', 1.6); grid on;
xlabel('x'); ylabel('f(x)'); title('Fonksiyon');

subplot(2,1,2);
semilogy(x, abs(dy_merkezi - dy_gercek) + eps, 'LineWidth', 1.2); hold on;
semilogy(x, abs(dy_ileri   - dy_gercek) + eps, 'LineWidth', 1.2); grid on;
xlabel('x'); ylabel('mutlak hata'); legend('merkezi fark','ileri fark');
title('Merkezi fark neden tercih edilir');

%% --- Interpolasyon: seyrek olcumden ara deger ---
x_olcum = linspace(a, b, 9);
y_olcum = f(x_olcum);
x_ince  = linspace(a, b, 400);
y_lin   = interp1(x_olcum, y_olcum, x_ince, 'linear');
y_spl   = interp1(x_olcum, y_olcum, x_ince, 'spline');
fprintf('\nDogrusal interp. maks hata : %.4e\n', max(abs(y_lin - f(x_ince))));
fprintf('Spline interp.  maks hata : %.4e\n', max(abs(y_spl - f(x_ince))));

function I = simpson(x, y)
    % Simpson kurali; nokta sayisi tek olmali
    n = numel(x);
    if mod(n,2) == 0
        x = x(1:end-1); y = y(1:end-1); n = n - 1;
    end
    h = (x(end) - x(1)) / (n - 1);
    I = h/3 * (y(1) + 4*sum(y(2:2:end-1)) + 2*sum(y(3:2:end-2)) + y(end));
end
""",
    "Simpson kurali duzgun fonksiyonlarda trapezden cok daha hizli yakinsar.",
    "Simpson's rule converges much faster than trapezoid for smooth functions.")


tpl("animasyon", "Hareket animasyonu ve video kaydi",
    "Motion animation and video export",
    "animasyon|hareketi canlandir|video|gif kaydet|simulasyon gorsel|"
    "animation|animate|movie|drawnow",
    r"""clear; clc; close all;

%% Iki boyutlu sarkac animasyonu (buyuk aci, dogrusal olmayan)
L = 1.0;  g = 9.81;
f = @(t, y) [y(2); -(g/L)*sin(y(1))];

[t, y] = ode45(f, linspace(0, 10, 600), [2.5; 0]);   % 2.5 rad ~ 143 derece
th = y(:,1);

x =  L*sin(th);
yk = -L*cos(th);

fig = figure('Color','w');
axis equal; grid on; hold on;
xlim([-1.2*L 1.2*L]); ylim([-1.2*L 0.4*L]);
xlabel('x [m]'); ylabel('y [m]'); title('Dogrusal olmayan sarkac');

cubuk = plot([0 x(1)], [0 yk(1)], 'k-', 'LineWidth', 2);
top   = plot(x(1), yk(1), 'ro', 'MarkerSize', 14, 'MarkerFaceColor','r');
iz    = plot(x(1), yk(1), 'b:', 'LineWidth', 1);

kaydet = false;          % true yaparsan sarkac.gif dosyasi olusur
for k = 1:4:numel(t)
    set(cubuk, 'XData', [0 x(k)], 'YData', [0 yk(k)]);
    set(top,   'XData', x(k),     'YData', yk(k));
    set(iz,    'XData', x(1:k),   'YData', yk(1:k));
    drawnow limitrate;

    if kaydet
        kare = getframe(fig);
        [A, harita] = rgb2ind(frame2im(kare), 256);
        if k == 1
            imwrite(A, harita, 'sarkac.gif', 'gif', 'LoopCount', Inf, ...
                    'DelayTime', 0.03);
        else
            imwrite(A, harita, 'sarkac.gif', 'gif', 'WriteMode', 'append', ...
                    'DelayTime', 0.03);
        end
    end
end

%% --- Enerji korunumu kontrolu: animasyon dogru mu? ---
E = 0.5*L^2*y(:,2).^2 + g*L*(1 - cos(y(:,1)));
fprintf('Enerji sapmasi: %%%.4f\n', 100*(max(E)-min(E))/mean(E));
""",
    "drawnow limitrate cizimi hizlandirir; her kareyi cizmek yerine adim atla.",
    "Use drawnow limitrate and skip frames to keep the animation fast.")


tpl("veri_isleme", "Olcum dosyasi okuma, temizleme ve ozetleme",
    "Reading, cleaning and summarizing measurement data",
    "veri oku|dosya oku|csv|excel|olcum dosyasi|tablo|veri temizleme|"
    "aykiri deger|read data|import|table|outlier|clean data",
    r"""clear; clc; close all;

%% --- Ornek veri uret (gercekte readtable ile dosyadan okunur) ---
% Gercek kullanim:
%   T = readtable('olcum.csv');            % MATLAB
%   M = csvread('olcum.csv', 1, 0);        % Octave
rng(7);
t     = (0:0.01:10).';
gercek = 3.2*exp(-0.25*t) .* sin(2*pi*0.8*t);
olcum  = gercek + 0.15*randn(size(t));
olcum(round([120 455 780])) = [9; -8; 11];      % aykiri degerler
olcum(round([300 301 302])) = NaN;              % eksik olcumler

fprintf('Ham veri : %d nokta, %d eksik\n', numel(olcum), sum(isnan(olcum)));

%% --- 1) Eksik degerleri doldur ---
gecerli = ~isnan(olcum);
temiz   = interp1(t(gecerli), olcum(gecerli), t, 'linear');

%% --- 2) Aykiri degerleri isaretle (medyan mutlak sapma yontemi) ---
med  = median(temiz);
mad  = median(abs(temiz - med));
esik = 3 * 1.4826 * mad;              % 1.4826: normal dagilim duzeltmesi
aykiri = abs(temiz - med) > esik;
fprintf('Aykiri deger sayisi: %d\n', sum(aykiri));
temiz(aykiri) = interp1(t(~aykiri), temiz(~aykiri), t(aykiri), 'linear');

%% --- 3) Gurultuyu azalt (hareketli ortalama) ---
pencere = 15;
suzulmus = movmean(temiz, pencere);

%% --- 4) Ozet istatistikler ---
fprintf('\nOrtalama : %8.4f\n', mean(suzulmus));
fprintf('Std sapma: %8.4f\n', std(suzulmus));
fprintf('En buyuk : %8.4f  (t = %.2f s)\n', max(suzulmus), t(find(suzulmus==max(suzulmus),1)));
fprintf('RMS hata : %8.4f\n', sqrt(mean((suzulmus - gercek).^2)));

figure('Color','w');
plot(t, olcum, '.', 'Color', [0.7 0.7 0.7]); hold on; grid on;
plot(t, suzulmus, 'LineWidth', 1.8);
plot(t, gercek, 'k--', 'LineWidth', 1.2);
xlabel('t [s]'); ylabel('deger');
legend('ham olcum','temizlenmis','gercek deger','Location','best');
title('Olcum verisi temizleme');
""",
    "Aykiri deger elemede ortalama+std yerine medyan+MAD kullan: aykiri degerler ortalamayi kendisi bozar.",
    "Use median+MAD instead of mean+std for outliers: outliers corrupt the mean itself.")


tpl("termo_cevrim", "Termodinamik cevrim ve P-V diyagrami",
    "Thermodynamic cycle and P-V diagram",
    "termodinamik cevrim|pv diyagrami|carnot cevrimi|otto cevrimi|"
    "isi makinesi|motor verimi|thermodynamic cycle|pv diagram|heat engine",
    r"""clear; clc; close all;

%% Carnot cevrimi — ideal gaz
R  = 8.314;      % [J/(mol*K)]
n  = 1;          % mol
Th = 600;        % sicak kaynak [K]
Tc = 300;        % soguk kaynak [K]
V1 = 0.010;      % [m^3]
V2 = 0.020;      % izotermal genlesme sonu
gam = 5/3;       % tek atomlu ideal gaz

% Adyabatik genlesme sonu: Th*V2^(g-1) = Tc*V3^(g-1)
V3 = V2 * (Th/Tc)^(1/(gam-1));
V4 = V1 * (Th/Tc)^(1/(gam-1));

P = @(V, T) n*R*T ./ V;

%% --- Dort kol ---
Va = linspace(V1, V2, 200);  Pa = P(Va, Th);                        % izotermal genlesme
Vb = linspace(V2, V3, 200);  Pb = P(V2,Th) * (V2./Vb).^gam;         % adyabatik genlesme
Vc = linspace(V3, V4, 200);  Pc = P(Vc, Tc);                        % izotermal sikistirma
Vd = linspace(V4, V1, 200);  Pd = P(V4,Tc) * (V4./Vd).^gam;         % adyabatik sikistirma

%% --- Isi ve is ---
Qh = n*R*Th*log(V2/V1);            % sicak kaynaktan alinan
Qc = n*R*Tc*log(V3/V4);            % soguk kaynaga verilen
W  = Qh - Qc;
verim      = W / Qh;
verim_teori = 1 - Tc/Th;

fprintf('Alinan isi  Qh = %8.2f J\n', Qh);
fprintf('Verilen isi Qc = %8.2f J\n', Qc);
fprintf('Net is      W  = %8.2f J\n', W);
fprintf('Verim          = %%%.3f\n', 100*verim);
fprintf('Carnot verimi  = %%%.3f   (fark %.2e)\n', 100*verim_teori, abs(verim-verim_teori));

%% --- Cevrimin alani ile isi dengesi tutuyor mu? ---
V_kapali = [Va Vb Vc Vd];
P_kapali = [Pa Pb Pc Pd];
W_alan   = -trapz(V_kapali, P_kapali);      % kapali egri alani
fprintf('P-V alanindan is = %8.2f J  (sapma %.3f%%)\n', W_alan, 100*abs(W_alan-W)/W);

figure('Color','w');
plot(Va,Pa,'r','LineWidth',2); hold on; grid on;
plot(Vb,Pb,'b','LineWidth',2);
plot(Vc,Pc,'m','LineWidth',2);
plot(Vd,Pd,'k','LineWidth',2);
fill(V_kapali, P_kapali, [0.9 0.95 1], 'FaceAlpha', 0.4, 'EdgeColor','none');
xlabel('Hacim V [m^3]'); ylabel('Basinc P [Pa]');
title(sprintf('Carnot cevrimi — verim %%%.1f', 100*verim));
legend('izotermal genlesme','adyabatik genlesme','izotermal sikistirma', ...
       'adyabatik sikistirma','net is','Location','best');
""",
    "Kapali P-V egrisinin alani net isi verir; bu, hesabin bagimsiz kontrolüdür.",
    "The enclosed P-V area equals the net work — an independent check on the calculation.")


tpl("optik_isin", "Isin izleme: mercek ve prizmadan gecen isik",
    "Ray tracing through lenses and prisms",
    "isin izleme|mercek simulasyonu|isik yolu|optik tasarim|prizma|mercek|"
    "isin|odaklama|dispersiyon|ray tracing|lens simulation|optical path|focal",
    r"""clear; clc; close all;

%% --- Ince mercek: paralel isinlarin odaklanmasi ---
f  = 0.10;                      % odak uzakligi [m]
h  = linspace(-0.04, 0.04, 9);  % gelen isinlarin yuksekligi
x0 = -0.15;

figure('Color','w');
subplot(1,2,1); hold on; grid on; axis equal;
for k = 1:numel(h)
    % Mercege kadar paralel
    plot([x0 0], [h(k) h(k)], 'b', 'LineWidth', 1);
    % Mercekten sonra: odak noktasindan gecer (ince mercek yaklasimi)
    egim = -h(k)/f;
    x_son = 0.25;
    plot([0 x_son], [h(k), h(k) + egim*x_son], 'b', 'LineWidth', 1);
end
plot([0 0], [-0.06 0.06], 'k', 'LineWidth', 3);      % mercek
plot(f, 0, 'ro', 'MarkerFaceColor','r');             % odak
text(f, 0.008, ' F', 'FontWeight','bold');
xlabel('x [m]'); ylabel('y [m]'); title('Ince mercekle odaklama');

%% --- Prizmada renk ayrismasi (dispersiyon) ---
% Cam icin Cauchy bagintisi: n(lam) = A + B/lam^2
A = 1.5220; B = 4.59e3;         % lam nanometre cinsinden
lam = [400 450 500 550 600 650 700];     % nm
n   = A + B ./ lam.^2;

tepe_aci = 60;                   % prizma tepe acisi [derece]
gelis    = 45;                   % gelis acisi [derece]

th1 = deg2rad(gelis);
Ap  = deg2rad(tepe_aci);
sapma = zeros(size(n));
for k = 1:numel(n)
    th2 = asin(sin(th1)/n(k));            % 1. yuzde kirilma
    th3 = Ap - th2;                       % ic geometri
    arg = n(k)*sin(th3);
    if abs(arg) <= 1
        th4 = asin(arg);                  % 2. yuzden cikis
        sapma(k) = rad2deg(th1 + th4 - Ap);
    else
        sapma(k) = NaN;                   % tam ic yansima
    end
end

fprintf('Dalga boyu   Kirilma indisi   Sapma acisi\n');
for k = 1:numel(lam)
    fprintf('  %4d nm        %.5f        %.3f derece\n', lam(k), n(k), sapma(k));
end
fprintf('Mor-kirmizi sapma farki: %.3f derece\n', abs(sapma(1)-sapma(end)));

renk = [0.5 0 0.8; 0 0 1; 0 0.7 1; 0 0.8 0; 1 0.9 0; 1 0.5 0; 1 0 0];
subplot(1,2,2); hold on; grid on;
for k = 1:numel(lam)
    plot(lam(k), sapma(k), 'o', 'MarkerSize', 10, ...
         'MarkerFaceColor', renk(k,:), 'MarkerEdgeColor','k');
end
plot(lam, sapma, 'k:', 'LineWidth', 1);
xlabel('Dalga boyu [nm]'); ylabel('Sapma acisi [derece]');
title('Prizmada dispersiyon: mor en cok sapar');
""",
    "Kisa dalga boyunda kirilma indisi buyuktur; bu yuzden mor isik en cok sapar.",
    "Refractive index is larger at short wavelengths, so violet bends the most.")


# ── Kimya ve biyoloji sablonlari ────────────────────────────────────────────
# Kullanici MATLAB'in yalnizca fizikte degil kimya ve biyolojide de ise
# yaramasini istedi. Bu ucu de ayni sayisal yontemleri kullanir: ODE
# cozumu, ustel iliskiler, rastgele yuruyus.

tpl("aksiyon_potansiyeli", "Aksiyon potansiyeli (Hodgkin-Huxley)",
    "Action potential (Hodgkin-Huxley)",
    "aksiyon potansiyeli|sinir hucresi|hodgkin huxley|noron simulasyonu|"
    "zar potansiyeli|sinir iletimi|action potential|neuron|membrane potential",
    r"""clear; clc; close all;

%% --- Hodgkin-Huxley modeli: kalamar dev aksonu (1952) ---
% Zar bir KONDANSATOR, iyon kanallari DIRENC. Denklem:
%   C dV/dt = I_uyari - I_Na - I_K - I_sizinti

C   = 1.0;      % zar kapasitansi [uF/cm^2]
gNa = 120;      % [mS/cm^2]
gK  = 36;
gL  = 0.3;
ENa = 50;       % denge potansiyelleri [mV]
EK  = -77;
EL  = -54.4;

%% --- Kapi degiskenlerinin hiz katsayilari ---
an = @(V) 0.01*(V+55)./(1-exp(-(V+55)/10));
bn = @(V) 0.125*exp(-(V+65)/80);
am = @(V) 0.1*(V+40)./(1-exp(-(V+40)/10));
bm = @(V) 4.0*exp(-(V+65)/18);
ah = @(V) 0.07*exp(-(V+65)/20);
bh = @(V) 1./(1+exp(-(V+35)/10));

%% --- Uyari akimi: 2 ms suren darbeler ---
I = @(t) 10*(mod(t,20) < 2);      % [uA/cm^2]

hh = @(t,y) [ (I(t) - gNa*y(2)^3*y(3)*(y(1)-ENa) ...
                    - gK*y(4)^4*(y(1)-EK) - gL*(y(1)-EL)) / C
              am(y(1))*(1-y(2)) - bm(y(1))*y(2)
              ah(y(1))*(1-y(3)) - bh(y(1))*y(3)
              an(y(1))*(1-y(4)) - bn(y(1))*y(4) ];

V0 = -65;
y0 = [V0; am(V0)/(am(V0)+bm(V0)); ah(V0)/(ah(V0)+bh(V0)); ...
      an(V0)/(an(V0)+bn(V0))];

[t,y] = ode15s(hh, [0 60], y0);

%% --- Cizim ---
subplot(2,1,1);
plot(t, y(:,1), 'LineWidth', 1.6); grid on;
xlabel('Zaman [ms]'); ylabel('Zar potansiyeli [mV]');
title('Aksiyon potansiyeli: esik asilinca hepsi-ya-da-hicbiri');
yline(-55, 'r--', 'esik');

subplot(2,1,2);
plot(t, y(:,2), t, y(:,3), t, y(:,4), 'LineWidth', 1.2); grid on;
legend('m (Na acilma)','h (Na kapanma)','n (K acilma)');
xlabel('Zaman [ms]'); ylabel('Kapi degiskeni');

fprintf('Tepe potansiyeli: %.1f mV\n', max(y(:,1)));
""",
    "Sodyum kanali hizli acilir (m), yavas kapanir (h); potasyum (n) gecikmeli "
    "acilip repolarize eder. Tepe yaklasik +40 mV cikar.",
    "Fast Na activation, slow inactivation and delayed K rectification give the "
    "spike; the peak reaches about +40 mV.")

tpl("tepkime_kinetigi", "Tepkime kinetigi ve Arrhenius",
    "Reaction kinetics and Arrhenius",
    "tepkime kinetigi|arrhenius|aktivasyon enerjisi|reaksiyon hizi|"
    "kimyasal kinetik|katalizor etkisi|reaction kinetics|activation energy",
    r"""clear; clc; close all;

%% --- Arrhenius: k = A*exp(-Ea/(R*T)) ---
R  = 8.314;            % [J/(mol*K)]
A  = 1e13;             % carpisma carpani [1/s]
Ea = [50e3, 75e3];     % katalizorlu / katalizorsuz [J/mol]
T  = linspace(273, 373, 200);

k = zeros(numel(Ea), numel(T));
for i = 1:numel(Ea)
    k(i,:) = A*exp(-Ea(i)./(R*T));
end

subplot(1,2,1);
semilogy(T-273.15, k, 'LineWidth', 1.6); grid on;
xlabel('Sicaklik [\circC]'); ylabel('Hiz sabiti k [1/s]');
legend('Ea = 50 kJ/mol (katalizorlu)','Ea = 75 kJ/mol');
title('Arrhenius: hiz sicaklikla USTEL artar');

%% --- 10 derecelik artis hizi kac kat buyutur? ---
T1 = 298; T2 = 308;
oran = exp(Ea(1)/R*(1/T1 - 1/T2));
fprintf('25 -> 35 C: hiz %.2f kat artar\n', oran);

%% --- Zaman icinde derisim: A -> B, birinci mertebe ---
k298 = A*exp(-Ea(1)/(R*T1));
odef = @(t,c) [-k298*c(1); k298*c(1)];
[t,c] = ode45(odef, [0 5/k298], [1; 0]);

subplot(1,2,2);
plot(t, c, 'LineWidth', 1.6); grid on;
xlabel('Zaman [s]'); ylabel('Derisim [mol/L]');
legend('[A]','[B]'); title('Birinci mertebe tepkime');
""",
    "exp(-Ea/RT) tam olarak Boltzmann carpanidir: engeli asabilen "
    "molekullerin oranini sayar. Katalizor Ea'yi dusurur, dengeyi degil.",
    "The Arrhenius exponential is the Boltzmann factor; a catalyst lowers Ea "
    "without shifting the equilibrium.")

tpl("difuzyon_brown", "Brown hareketi ve difuzyon",
    "Brownian motion and diffusion",
    "brown hareketi|difuzyon|rastgele yuruyus|molekuler tasima|"
    "einstein stokes|brownian motion|diffusion|random walk",
    r"""clear; clc; close all;

%% --- Einstein-Stokes: D = kT/(6*pi*eta*r) ---
kB  = 1.380649e-23;
T   = 300;             % [K]
eta = 1.0e-3;          % suyun viskozitesi [Pa*s]
r   = 5e-9;            % protein yaricapi [m]
D   = kB*T/(6*pi*eta*r);
fprintf('Difuzyon katsayisi D = %.3e m^2/s\n', D);

%% --- Rastgele yuruyus: 500 parcacik, 2 boyut ---
N = 500; adim = 2000; dt = 1e-4;
sigma = sqrt(2*D*dt);
x = zeros(N,adim); y = zeros(N,adim);
for k = 2:adim
    x(:,k) = x(:,k-1) + sigma*randn(N,1);
    y(:,k) = y(:,k-1) + sigma*randn(N,1);
end

t = (0:adim-1)*dt;
msd = mean(x.^2 + y.^2, 1);       % ortalama kare yer degistirme

subplot(1,2,1);
plot(x(1:20,:)'*1e6, y(1:20,:)'*1e6); grid on; axis equal;
xlabel('x [\mum]'); ylabel('y [\mum]');
title('Rastgele yuruyus: 20 parcacigin izi');

subplot(1,2,2);
plot(t, msd, 'LineWidth', 1.6); hold on;
plot(t, 4*D*t, 'r--', 'LineWidth', 1.4); grid on;
xlabel('Zaman [s]'); ylabel('<r^2> [m^2]');
legend('simulasyon','4Dt (kuram)', 'Location','northwest');
title('Yer degistirme zamanla DOGRUSAL buyur');

%% --- 10 mikronluk hucreyi gecme suresi ---
L = 10e-6;
fprintf('%.1f mikron yolu difuzyonla gecme suresi: %.2f s\n', L*1e6, L^2/(2*D));
""",
    "Difuzyonda yol degil KARESI zamanla dogrusal buyur; bu yuzden mesafe "
    "iki katina cikinca sure dort katina cikar.",
    "Mean square displacement grows linearly in time, so doubling the distance "
    "quadruples the time.")

tpl("planck_spektrum", "Kara cisim isinimi (Planck egrisi)",
    "Blackbody radiation (Planck curve)",
    "kara cisim|planck egrisi|isima spektrumu|wien yasasi|stefan boltzmann|"
    "blackbody|planck curve|radiation spectrum",
    r"""clear; clc; close all;

%% --- Planck yasasi ---
h  = 6.62607015e-34;  c = 2.99792458e8;  kB = 1.380649e-23;
lam = linspace(1e-8, 3e-6, 2000);          % [m]
T   = [3000 4500 5778 7000];               % [K] (5778 = Gunes)

B = @(l,Tt) 2*h*c^2 ./ (l.^5 .* (exp(h*c./(l*kB*Tt)) - 1));

hold on; grid on;
for Tt = T
    plot(lam*1e9, B(lam,Tt), 'LineWidth', 1.6);
end
xlabel('Dalga boyu [nm]'); ylabel('Spektral isima [W/m^3]');
legend(compose('%d K', T)); title('Planck egrisi: morotesi felaketi yok');

%% --- Wien ve Stefan-Boltzmann dogrulamasi ---
for Tt = T
    [~,i] = max(B(lam,Tt));
    fprintf('T = %5d K -> tepe %6.1f nm | Wien: %6.1f nm\n', ...
            Tt, lam(i)*1e9, 2.897771955e-3/Tt*1e9);
end
sigma = 5.670374419e-8;
fprintf('Gunes yuzeyi toplam isima: %.2e W/m^2\n', sigma*5778^4);
""",
    "Klasik kuram kisa dalga boyunda sonsuza giderdi; h ile kuantalanma "
    "yuksek frekansli modlari bastirir ve egri tepe yapip duser.",
    "Quantisation suppresses high-frequency modes, turning the diverging "
    "classical curve into a peaked spectrum.")


# ── Kodun anlatimi ──────────────────────────────────────────────────────────
# Kullanici "sadece kod veriyor, ogretmiyor" dedi. Asagidaki anlatim koddan
# TURETILIR: bolum basliklari kodun kendi `%% --- ... ---` satirlarindan,
# fonksiyon aciklamalari da asagidaki sozlukten gelir. Hicbir sey uydurulmaz,
# bu yuzden kod degistiginde anlatim da kendiliginden dogru kalir.

FONKSIYON_ACIKLAMA = {
    "ode45": ("degisken adimli Runge-Kutta ile diferansiyel denklem cozer",
              "solves ODEs with adaptive Runge-Kutta"),
    "ode15s": ("kati (stiff) diferansiyel denklemleri cozer",
               "solves stiff ODEs"),
    "fft": ("hizli Fourier donusumu — sinyali frekans bilesenlerine ayirir",
            "fast Fourier transform"),
    "eig": ("matrisin ozdeger ve ozvektorlerini bulur",
            "computes eigenvalues and eigenvectors"),
    "cond": ("kosul sayisi — sonucun sayisal olarak ne kadar guvenilir oldugu",
             "condition number: numerical reliability of the solution"),
    "norm": ("vektor/matris buyuklugu; kalinti olcmek icin kullanilir",
             "vector or matrix norm, used to measure residuals"),
    "trapz": ("yamuk kuraliyla sayisal integral alir",
              "numerical integration by the trapezoid rule"),
    "integral": ("uyarlanabilir sayisal integral (yuksek dogruluk)",
                 "adaptive numerical integration"),
    "interp1": ("bilinen noktalar arasinda ara deger uretir",
                "interpolates between known points"),
    "polyfit": ("en kucuk karelerle polinom uydurur",
                "least-squares polynomial fit"),
    "fzero": ("tek degiskenli bir fonksiyonun kokunu bulur",
              "finds a root of a scalar function"),
    "fminsearch": ("turevsiz en kucukleme (Nelder-Mead)",
                   "derivative-free minimization"),
    "linspace": ("iki deger arasinda esit araliki dizi uretir",
                 "evenly spaced vector between two values"),
    "meshgrid": ("iki boyutlu hesap icin koordinat izgarasi kurar",
                 "builds a 2-D coordinate grid"),
    "quiver": ("vektor alanini oklarla cizer", "plots a vector field"),
    "contour": ("es duzey egrilerini cizer", "draws contour lines"),
    "movmean": ("hareketli ortalama ile gurultuyu azaltir",
                "moving average smoothing"),
    "median": ("medyan — aykiri degerlerden etkilenmeyen orta deger",
               "median, robust against outliers"),
    "randn": ("normal dagilimli rastgele sayi uretir",
              "normally distributed random numbers"),
    "rng": ("rastgele sayi uretecini sabitler; sonuc tekrarlanabilir olur",
            "seeds the random generator for reproducibility"),
    "odeset": ("cozucu toleranslarini ayarlar", "sets solver tolerances"),
    "drawnow": ("cizimi aninda ekrana basar (animasyon icin)",
                "flushes the plot immediately, for animation"),
    "getframe": ("ekrandaki kareyi yakalar (video/gif icin)",
                 "captures the current frame"),
    "readtable": ("dosyadan tablo olarak veri okur",
                  "reads data from a file into a table"),
    "syms": ("sembolik degisken tanimlar", "declares symbolic variables"),
    "solve": ("denklemi sembolik olarak cozer", "solves an equation symbolically"),
    "diff": ("sembolik turev alir", "symbolic derivative"),
    "int": ("sembolik integral alir", "symbolic integral"),
    "roots": ("polinomun koklerini bulur", "roots of a polynomial"),
    "deg2rad": ("dereceyi radyana cevirir", "converts degrees to radians"),
    "trace": ("matrisin izi", "matrix trace"),
    "sparse": ("seyrek matris — bellek ve hiz kazanci",
               "sparse matrix for memory and speed"),
}

_BOLUM = re.compile(r"^%%\s*-*\s*(.+?)\s*-*\s*$", re.M)


def aciklama(key, lang="tr"):
    """Sablonun ne yaptigini adim adim anlat.

    Bolumler kodun kendi `%%` basliklarindan, fonksiyon aciklamalari
    FONKSIYON_ACIKLAMA sozlugunden gelir.
    """
    t = TEMPLATES.get(key)
    if not t:
        return ""
    tr = lang == "tr"
    kod = t["code"]

    bolumler = [b.strip() for b in _BOLUM.findall(kod)
                if b.strip() and not b.strip().startswith("%")]
    kullanilan = []
    for fn, (a_tr, a_en) in FONKSIYON_ACIKLAMA.items():
        if re.search(r"(?<![\w.])%s\s*\(" % re.escape(fn), kod):
            kullanilan.append((fn, a_tr if tr else a_en))

    lines = []
    if bolumler:
        lines.append("**" + ("Kod ne yapıyor" if tr else "What the code does")
                     + "**")
        lines.append("")
        for i, b in enumerate(bolumler[:8], 1):
            lines.append("%d. %s" % (i, b))
        lines.append("")
    if kullanilan:
        lines.append("**" + ("Kullanılan MATLAB fonksiyonları" if tr
                             else "MATLAB functions used") + "**")
        lines.append("")
        for fn, ack in kullanilan[:8]:
            lines.append("- `%s` — %s" % (fn, ack))
        lines.append("")
    if lines:
        lines.append(("_Parametreleri kodun başındaki değişkenlerden "
                      "değiştirip tekrar çalıştırabilirsiniz._" if tr else
                      "_Change the parameters at the top and re-run._"))
    return "\n".join(lines)
