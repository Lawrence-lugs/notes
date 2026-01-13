---
title: Generalized Eigenvalues in FEM Formulations
modified: 2026-01-12T14:50:03+08:00
date: 2025-9-18
---
# Generalized Eigenvalue Problem

The eigenvectors and eigenvalues of $\mathbf{M}$ and $\mathbf{K}$ can significantly simplify solutions of the FEM problem.

Decomposing the solution $u(x,t)$ into a linear combination of eigenvalues and eigenvectors allows to solve only the $N$ (like 20 or so) most important modalities. The rest of the eigenvectors contribute so little to $u(x,t)$ that numeric error outscales it, so they're not really necessary. 

We can look at the unforced FEM formulation of the heat equation for this:
$$\mathbf{M}\vec{\frac{du}{dt}}+\mathbf{K}\vec{u}=0$$
If we can find the eigenvector $\vec{v}$ of $\mathbf{K}$ and $\mathbf{M}$ with eigenvalue $\lambda$, we can just do:
Let $\vec{u}=\vec{v}e^{-\lambda t}$ (decay). Then,
$$-\mathbf{M}\lambda\vec{u}+\mathbf{K}\vec{u}=0$$
$$-\mathbf{M}\lambda\vec{v}e^{-\lambda t}+\mathbf{K}\vec{v}e^{-\lambda t}=0$$
$$-\mathbf{M}\lambda\vec{v}+\mathbf{K}\vec{v}=0$$
and we get that the $\lambda$ are the eigenvalues in a [generalized eigenvalue problem](https://en.wikipedia.org/wiki/Eigendecomposition_of_a_matrix#Generalized_eigenvalue_problem).

Then, we can use this in some Fourier or Laplace magic (in this case, laplace magic because the time-varying forms called $\xi(t)=e^{-\lambda t}$ are decay forms)

We can project the solution into a basis of a bunch of discrete $\lambda$ time constants and add up the solutions for each of those.

>[!tip] The Spectral Theorem
>In fact, the spectral theorem gives us that if $K$ and $M$ are symmetric positive-definite matrices, we can always get real $\lambda$ and that the eigenvectors $v_1,v_2,...,v_3$ form a basis.
>This means we can project the true solution into the basis.

So then, the exact solution becomes a linear combination of eigenvectors:
$$u(t)=\sum^{N}_{i=1} c_iv_ie^{-\lambda_it}$$
# Generalized eigenvalues with a force term

With a force term, we get something like 
$$-\mathbf{M}\lambda\vec{v}e^{-\lambda t}+\mathbf{K}\vec{v}e^{-\lambda t}=\mathbf{F}$$
In this case, the time term is incorrect (the forcing term prevents it from just being a decay, making the "guess" incorrect) 

So then, we just avoid guessing a time term completely.

Let $\vec{u}=\vec{v_i}\xi_i(t)$

Then we can use this in the FEM formulation
$$\mathbf{M} \left( \sum_{i=1}^N \dot{\xi}_i(t) \vec{v}_i \right) + \mathbf{K} \left( \sum_{i=1}^N \xi_i(t) \vec{v}_i \right) = \mathbf{F}(t)$$
To isolate the solution for a specific mode, $v_i$, we multiply with the ket form $v_j^T$ to "precipitate out" the important terms.
$$\vec{v}_j^T \mathbf{M} \left( \sum \dot{\xi}_i \vec{v}_i \right) + \vec{v}_j^T \mathbf{K} \left( \sum \xi_i \vec{v}_i \right) = \vec{v}_j^T \mathbf{F}(t)$$
That is, important terms being **only the ones with $i=j$**. For the other terms, 
$$v_j^T \mathbf{M} v_i=0 \text{ if }i \neq j \text{ (orthogonal basis)}$$
$$v_j^T \mathbf{K} v_i=0 \text{ if }i \neq j \text{ (orthogonal basis)}$$
We're left with the $\xi_i(t)$ terms mixed with a simple scalar form.
$$\vec{v}_j^T \mathbf{M} \vec{v}_j\dot{\xi}_j(t) + \vec{v}_j^T \mathbf{K} \vec{v}_j\xi_j(t)=\vec{v}_j^T\mathbf{F}(t)$$
We call these terms "modal mass, modal stiffness, and modal force":
$$m_j \dot{\xi}_j(t) + k_j \xi_j(t) = f_j(t)$$

> [!tip]
> Interestingly, these terms resemble the ket forms in quantum mechanics $$\bra{v}\mathbf{M}\ket{v}, \bra{v}\mathbf{K}\ket{v}, \bra{v}\mathbf{F}$$
> Apparetly $\bra{v}\mathbf{M}\ket{v}$ is called the kinetic energy norm and 
> $\bra{v}\mathbf{K}\ket{v}$ is called the Strain Energy

Now we have a simply solvable calculus problem:
$$\frac{d\xi_j}{dt}+\lambda_j\xi_j=\frac{f_j(t)}{m_j}$$
whose solution is
$$\xi_j(t)=\xi_j(0)e^{-\lambda_j t}+\int_0^td\tau e^{-\lambda_j (t-\tau)} \frac{f_j(\tau)}{m_j}$$

The thing is, we have to do that for *every single modality we're accounting for*. 

Maybe the good news is that solving for the $\xi_j$ form once probably makes it trivial to get all the others ($f_j$ will likely rarely change in form per $j$, more like only scaling)

> [!tip] For second-order FEM formulas 
> For things like the beam equation, for example, the solution turns out to be 
> $$\ddot{\xi} + \omega_0^2 \xi = f(t)$$
> $$\xi(t) = \int_0^t \frac{1}{\omega_0} \sin(\omega_0(t-\tau)) f(\tau) d\tau$$


# How to solve a generalized eigenvalue problem?

Starting from 
$$-\mathbf{M}\lambda\vec{v}+\mathbf{K}\vec{v}=0$$
we still need to solve for the $\lambda_j$s and the $\vec{v_j}$s. 

We use the Lanczos algorithm for this (kind of like Givens rotations etc. algorithms for QR decomposition.)


>[!note]
>This is nice because the Lanczos algorithm can give the eigenvalues in order of importants (like PCA).
>That's because it usually gives it in order of highest to lowest (like most linalg iterative algorithms) but if you do shift-and-invert you can make the lowest eigenvalues the highest.

# Where is this used?

Only used for problems with nice well-defined structures whose properties $\mathbf{M}$ and $\mathbf{K}$ do not change over the course of the simulation. 

Problems where it's applicable:

- Tall building (doesn't really change behavior until it breaks)
- PCB vibration
- Drivetrains and gears
- Laminar flow (apparently you just have the Stokes Equation for this)

Problems where it's inapplicable:

- Turbulent flow (you have to use Navier-Stokes, which has an advection $(\vec{v} \cdot \nabla) \vec{v}$ term that will appear as $\mathbf{K}(v)$. Stiffness is a function of $v$. For these, we have to directly solve the FEM form.

# Notes

> [!note]
> The eigenvalues $\lambda_i$ are not like harmonics- they can be randomly spaced in between each other. $\lambda_2$ might be $1.43 \times \lambda_1$. $\lambda_3$ might be $2.11 \times \lambda_1$.

> [!note]
> In practice, we choose some "Nyquist maximum" frequency at which to stop caring about the solution. So then we solve for all $\lambda_n < 1Grads$ or $\omega_n < 1Grads$ if we expect the forcing function $f$. 

> [!note] Cool thing:
> $\vec{v}_j^T\mathbf{F}(t)$ is literally use projecting the "simulation stimulus force" onto the eigenvector basis.
> So then putting specific modalities of vibration or decay in $F$ would allow us to simulate resonance type things.
> We're not turning $F$ into its fourier transform. Rather, we're asking how much does $F$ looks like $v_1$? How much does it look like $v_2$? etc.

# "Test coverage" and using eigenvalue-based FEM correctly:

>[!note] Effective Modal Inertia
>A parameter named "effective modal inertia" captures the "test coverage" of eigenvectors- capturing how much the current set of eigenvectors makes up the overall response to a stimulus $F$.
>
>Simulating with a specific $F$ like an earthquake you try to get up to 90% "test coverage" (effective modal inertia) on it. 
>
>Then, you think of another $F$ to test it out with. Say, supertyphoon winds, then you get 90% test coverage on that.
> 
> If you fail to find the $F$ that breaks your thing, that's unfortunate.

I have an idea.

I wonder if we can design $F$ to be "constant white noise" in the "eigenvector basis" so that we can use one $F$ to simulate all behaviors?

This is apparently called "Response Spectrum Analysis". Commercial simulators have this feature, as it looks like in Google results.

> Ok. Since we can disastrously miss resonance modes that can cause failure, let's just go back to the direct FEM solution.

For this one, we're limited instead by the $\Delta t$ used in the RK4 or the reverse euler solution. 