---
title: Minority Carrier Diffusion Equations with explicit FEM in C
modified: 2026-01-17
date: 2026-01-12T14:48:24+08:00
draft: true
---

>[!question] 
>- How do we deal with PDEs in the current RK4 setup?
>- What do we need to do to implement FEM in C?

# Finite Difference

Let's start with an easy formulation: minority carrier diffusion with RG 

$$\frac{dn}{dt}=D_n\frac{d^2n}{dx^2}-\frac{n}{\tau_n}$$
$$n\Big\vert_{x=0}=n_0;n\Big\vert_{t=0}=0$$
$$n\Big\vert_{x=L}=n_0$$
where $n$ is the minority carrier concentration.

>[!tip] Aside
>Why is diffusion second-order here? If it's diffusion, it should just depend on the concentration gradient, which is first-order.
>
>Intuitively, if the rate of flow of $n$ into a spot $x$ is $dn/dt$. If that's constant over $x$, the should be no change in concentration over time (inflow = outflow). However, if there is a difference in inflow and outflow (divergence) then there will be a $dn/dt$. By this logic:
>
>$$\frac{dn}{dt}=\vec\nabla\cdot\nabla n$$
>
>i.e. second derivative in one dimension

So we have a slope function of

$$\frac{dn}{dt}=D_n \frac{2n-n_{x+1}-n_{x-1}}{\Delta x^2}-\frac{n}{\tau_n}$$

As we introduce separate state vectors for every point $n_x$.

Now, we have a grid of $n_0,n_1,...,n_N$ separated by a $dx$.
## Constants

$$\frac{D_n}{\mu_n} = 0.026V$$
$$D_n=0.026V*1350\frac{cm^2}{Vs}=35 cm^2/s$$

## A tensor library isn't THAT necessary for Physics

I'm starting to regret coupling so closely to my tensor library.
1. State structs should just be per-application, now that I realize. It's a waste to use vectors for this.
2. Matrix multiplication was trivially coded. It's not even useful beyond the easy eigen-able formulations. As soon as quadratic drag was introduced, it was ggs. ($\propto v^2$).

Anyway, we still need tensors to keep track of complicated grids. However, we'll just be using the canonical main tensor definition.

```c
typedef struct Tensor {
    size_t length;
    size_t ndims;
    size_t* shape;
    float* elements;
} Tensor;
```

See [the current library here](https://github.com/Lawrence-lugs/diff_eq_solvers/blob/6c024e235c1a7bc91b499b3df740ba0da1ad151c/tensors.c#L1).

This ended up mainly useful for the global objects.

```c
    size_t tensorShape[3] = {2, NUM_GRID_POINTS, NUM_STEPS};
    Tensor* results = tensor_create(3, tensorShape);

    size_t gridShape[2] = {2, NUM_GRID_POINTS};
    Tensor* grid = tensor_create(2,gridShape);
    tensor_set_zero(grid);
```

## Prev, Current, Next Point Iteration

We take the current, previous and next points from the grid and compute the slope from that. Let's use forward euler for now.

>[!note] 
>Notice how we've stopped using vectors for state. This is us decoupling physics from the tensor library. We just use a function to transform the global tensor into state.

```c
    State currPointState = get_point_from_grid(grid_old, point);
    State prevPointState = get_point_from_grid(grid_old, point-1);
    State nextPointState = get_point_from_grid(grid_old, point+1);

    State slope = get_slope(currPointState, prevPointState, nextPointState);
    
    char name[32];
    char slope_name[32];
    sprintf(name, "Point %zu", point);
    sprintf(slope_name, "Slope %zu", point);

    printf("State %zu : (%f,%f)\n",point,currPointState.n,currPointState.dn);
    printf("Slope %zu : (%f,%f)\n",point,slope.n,slope.dn);

    currPointState.n = currPointState.n + DT*slope.n;
    currPointState.dn = currPointState.dn + DT*slope.dn;

    insert_state_on_grid(grid, point, currPointState);
```

The PDE is encoded in the get_slope function as usual.

```c
State get_slope(const State point, const State leftPoint, const State rightPoint) {

    State slope;
    float diffusion    = -DIFFN*(2*point.n-leftPoint.n-rightPoint.n)/(DX*DX);
    float rg           = - point.n/TAU;
    slope.n = point.dn;
    slope.dn = rg; 
    return slope;

}
```

>[!warning] Debug 
>- Trying to copy 3200b into a 400b location. - something wrong with `tensor_length`
>- Trying to copy 400b into an 8b location. - `tensor_sliceto` wasn't calculating an offset
>- Tensor copy shape mismatch (some large number != 2) - probs initializing shape?

```log
Tensor copy shape 0 mismatch (tsr1 1203982336 != tsr2 2)
[1203982336,2]
```

# Weak Form of Minority Carrier Diffusion

# Finite Element

