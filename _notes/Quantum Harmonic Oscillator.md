---
title: The Quantum Harmonic Oscillator has Energy Quanta (Shocking, I know)
toc: true
modified: 2026-01-18
date: 2025-12-12
---
# There must be a number operator, right?!
The hamiltonian/energy operator for the quantum harmonic oscillator is 
$$\hat{H} =-\frac{\hat{p}^2}{2m}+\frac{m\omega\hat{x}^2}{2}$$
$$\hat{H} =\frac{m\omega^2}{2}(\hat{x}^2-\frac{\hat{p}^2}{m^2\omega^2})$$
We know from the quantum revolution that the energy is a multiple of some quantum ground state $\frac{\hbar\omega}{2}$ (zero-point energy of the heisenberg uncertainty principle). Hence, we introduce the number operator that hopefully gives that specific "number". This form can do that for us:
$$\hat{H}=\hbar\omega(\hat{n}+\frac{1}{2})$$
Because things in the quantum realm are positive-definite and the number operator is hermitian (why?), the number operator must be Cholesky decomposable:
$$\hat{n}=\hat{a}^\dagger\hat{a}$$
In the first place we were tempted to factor the Hamiltonian, so this is good. Then, we can try to see how we can transform the Hamiltonian into these factors.
$$\hat{n}=\frac{m\omega}{2\hbar}(\hat{x}^2-\frac{\hat{p}^2}{m^2\omega^2})-\frac{1}{2}$$
We observe that there must be "gunk" left over as $1/2$. This maybe comes from the commutator junk. Let's see. Anyway, we can then define:
$$\hat{a}^\dagger=\sqrt{\frac{m\omega}{2\hbar}}(\hat{x}-\frac{i\hat{p}}{m\omega})$$
$$\hat{a}=\sqrt{\frac{m\omega}{2\hbar}}(\hat{x}+\frac{i\hat{p}}{m\omega})$$
Let's confirm the commutator junk:
$$\hat{a}^\dagger\hat{a}=\frac{m\omega}{2\hbar}(\hat{x}^2+\frac{\hat{p}^2}{m^2\omega^2}+i\frac{\hat{x}\hat{p}-\hat{p}\hat{x}}{m\omega})$$
and since $[\hat{x},\hat{p}]=i\hbar$,
$$\hat{a}^\dagger\hat{a}=\frac{m\omega}{2\hbar}(\hat{x}^2+\frac{\hat{p}^2}{m\omega})-\frac{1}{2}$$
which we can plug into the original and see that it's correct.

# Annihilation and Creation by Coincidence

By coincidence, the Cholesky decomposition of the number operator somehow are the annihilation and creation operators. We find this out by smashing the operators into the eigenvector $\ket{n}$.

We define $\ket{n}$ as the wavefunction at level $n$.

So then, $\hat{n}\ket{n}=n\ket{n}$

As an aside, we tried smashing the annihilation and destruction operators together and found that:
$$[\hat{a},a^\dagger]=\hat{a}\hat{a}^\dagger-\hat{a}^\dagger\hat{a}=1$$
$$\hat{n}=\hat{a}\hat{a}^\dagger-1$$
Now let's see what happens to the wavefunction number if we apply just part of the number operator:
$$\hat{n}\hat{a}\ket{n}=(\hat{a}\hat{a}^\dagger-1)\hat{a}\ket{n}=(\hat{a}\hat{n}-\hat{a})\ket{n}=(n-1)\hat{a}\ket{n}$$
and wow, it turns out that the $\hat{a}\ket{n}$ has a number of $n-1$!
$$\hat{n}\hat{a}^\dagger\ket{n}=\hat{a}^\dagger\hat{a}\hat{a}^\dagger\ket{n}=\hat{a}^\dagger(\hat{n}+1)\ket{n}=(n+1)\hat{a}^\dagger\ket{n}$$
and wow, it turns out that $\hat{a}^\dagger\ket{n}$ has a number of $n+1$!

# normalization

But wait! We never said the annihilation and creation operators would end up with normalized eigenvectors!

By choice, $\ket{n}$ is already normalized, and so would $\ket{n-1}$ or $\ket{n+1}$ and any other specially named "state at this level $n$".

So then, we need to reconcile the creation operators by finding the multiplier that makes sure the result is actually the normalized $\ket{n-1}$.

$$\hat{a}\ket{n}=k\ket{n-1}$$
$$\bra{n}\hat{a}^\dagger\hat{a}\ket{n}=n=k^2\braket{n-1|n-1}=k^2$$
$$k=\sqrt{n}$$
$$\hat{a}\ket{n}=\sqrt{n}\ket{n-1}$$

Next, for the creation operator, the result has to be a normalized $\ket{n+1}$:
$$\hat{a}^\dagger\ket{n}=k\ket{n+1}$$
$$\bra{n}\hat{a}\hat{a}^\dagger\ket{n}=\underbrace{n+1}_{\hat{n}+1=\hat{a}\hat{a}^\dagger}=k^2\braket{n+1|n+1}$$
$$k=\sqrt{n+1}$$
$$\hat{a}^\dagger\ket{n}=\sqrt{n+1}\ket{n+1}$$
So stuff like these are true:
$$\hat{a}\ket{1}=1\ket{0}=\ket{0}$$
$$\hat{a}^\dagger\ket{0}=\ket{1}$$
$$\hat{a}^\dagger\ket{1}=\sqrt{2}\ket{2}$$
$$\hat{a}\ket{0}=0\ket{-1}=0$$
This is why it's called the annihilation operator.

>[!tip] Building from the ground state
>This means that
>$$\ket{n}=\frac{\hat{n}^{\dagger n}}{\sqrt{n!}}\ket{0}$$

> [!warning] Hmm...
> So then we can "lose" a wavefunction by annihilating it too much.
> $$\hat{a}\ket{0}=0$$
> and
> $$\hat{a}^\dagger0=0$$
> you can't create back what's been annihilated (oof).
> 
> In linear algebra terms, $\hat{a}$ has a nontrivial kernel (some subspace of the vector space is turning into the null vector i.e. *a null space exists*). $\hat{a}^\dagger$ has a trivial kernel, because its null space is just the null vector i.e. there is no input to $\hat{a}^\dagger$ that equals $0$ other than $0$ itself.
> 
> The commutator being nonzero is related to the existence of this nullspace for $\hat{a}$.

# Phonons

Take an example of a set of point masses connected by springs with constant $K$. Then, the hamiltonian would be:

$$\hat{H}=\sum_{j=0}^N\frac{\hat{p_j}^2}{2m}+\frac{K(\hat{x_{j+1}}-\hat{x}_j)^2}{2}$$

Then, we can take the fourier transforms of the position and momentum operators:

$$x_j=
\frac{1}{\sqrt{N}}
\sum_k\tilde{x_k}e^{ikja}
$$
$$p_j=
\frac{1}{\sqrt{N}}
\sum_k \tilde{p_k}e^{ikja}$$
If we impose periodic boundary conditions $e^{ikja}=e^{ik(j+N)a}$ (that is, this must be periodic with period $j_N$ or as in looping through all the points will bring you back to the first one) then 

$$\sum_j e^{ikja}=N\delta_{k,0}$$