# DDM theory

To obtain $A$ and $B$ when performing DDM some Fourier analysis is required. Starting from the definition of the image structure function, 

$$
	\begin{equation}
		
		D(\vec{q}, t) = A(\vec{q})(1-f(\vec{q}, t) + B(\vec{q}),
	\end{equation}
$$ (eq:dNormal)

which is calculated as

$$
	\begin{equation}		
		D(\vec{q}, t) = \langle|\tilde{I}(\vec{q}, t + \tau) - \tilde{I}(\vec{q}, t)|^2\rangle_t.
	\end{equation}
$$ (eq:dFull)

Here, $\tilde{I}(\vec{q}, t)$ is the Fourier transform of the image at time $t$ and $\tau$ is the lag time. By expanding equation {eq}`eq:dFull` we can write this as

$$
\begin{equation}
	D(\vec{q}, t) = 2\langle|\tilde{I}(\vec{q}, t)|^2\rangle_t - 2\langle\Re[\tilde{I}(\vec{q}, t+ \tau)\tilde{I}^\ast(\vec{q}, t)]\rangle_t.
\end{equation}
$$ (eq:dExpanded)

To get to this point, there is a simplification made that $\langle|\tilde{I}(\vec{q}, t+\tau)|^2\rangle_t$ is independent on $\tau$, i.e. $\langle|\tilde{I}(\vec{q}, t+\tau)|^2\rangle_t = \langle|\tilde{I}(\vec{q}, t)|^2\rangle_t$. By comparing terms dependent and independent of $\tau$ in equations {eq}`eq:dExpanded` and {eq}`eq:dNormal`, one can write

$$
\begin{equation}
	A(\vec{q}) + B(\vec{q}) = 2\langle|\tilde{I}(\vec{q}, t)|^2\rangle_t
\end{equation}
$$ (eq:aPlusb)

and

$$
\begin{equation}
	A(\vec{q})f(\vec{q}, t) = 2\langle\Re[\tilde{I}(\vec{q}, t+ \tau)\tilde{I}^\ast(\vec{q}, t)]\rangle_t.
\end{equation}
$$ (eq:af)

At this point we can do one of two things. Firstly, we can assume that at very large $q$, $A(\vec{q}) = 0$. This is because $A$ represents an amplitude term which depends on spatial intensity correlations. Therefore one can calculate

$$
\begin{equation}
	B(\vec{q}; q \to \infty) = 2\langle|\tilde{I}(\vec{q}; q \to \infty, t)|^2\rangle_t,
\end{equation}
$$

where $q = |\vec{q}|$. It is then simple to calculate $A(\vec{q})$ for all $\vec{q}$ from equation {eq}`eq:aPlusb`.

Alternatively, we can use _a priori_ knowledge of the Intermediate Scattering Function (ISF), $f(\vec{q}, \tau)$ to say that $f(\vec{q}, \tau \to 0)$. With this and equation {eq}`eq:af` we can calculate $A(\vec{q})$ as

$$
\begin{equation}
	A(\vec{q}) = \lim_{\tau\to 0}2\langle\Re[\tilde{I}(\vec{q}, t+ \tau)\tilde{I}^\ast(\vec{q}, t)]\rangle_t.
\end{equation}
$$
