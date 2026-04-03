---
title: Solving Ballistics Equation with RK4 in C
modified: 2026-01-15
date: 2026-01-12
toc: true
---
>[!note] Questions
> - How do we encode the ballistics equation in C?

So the most basal ballistics equation is
$$\mathbf{F}=m\vec{a}$$

Then the vectors are $\mathbf{F},x,y,\frac{dx}{dt},\frac{dy}{dt}$. The state vector 
$$\vec{S}=\begin{bmatrix}
x\\y\\dx/dt\\dy/dt
\end{bmatrix}$$ 
# Forward Euler
![](attachments/Pasted%20image%2020260115115215.png)
$$\vec{S}_{n+1}=\mathbf{U}\vec{S_n}+\vec{F}$$
and since $x_{n+1}=\Delta t \frac{dx}{dt}+x_n,y_{n+1}=\Delta t \frac{dy}{dt}+y_n,$

The update matrix is
$$\mathbf{U}=\begin{bmatrix}
1 & 0 & dt & 0 \\
0 & 1 & 0 & dt \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 \\
\end{bmatrix}, \vec{F}=\begin{bmatrix}
0 \\ 0 \\ 0 \\ -g\cdot dt
\end{bmatrix}$$

So first let's try to make some vector-matrix working and test it out

```c
#include <stdio.h>
#include <stdlib.h>

// Not sure if it's a good idea to name these such a generic name
// How do we handle other datatypes of vectors?
typedef struct vector {
    size_t length;
    float* elements; 
} vector_t;

typedef struct matrix {
    size_t rows;
    size_t cols;
    float* elements;
} matrix_t;

// Any naming scheme for this to keep it local? 
// There aren't any classes in C, but I've heard 
// significant criticism of C++ anyway.
float matrix_get_element (matrix_t* mat, int i, int j) {

    if (i > mat->rows || j > mat->cols) {
        // Don't know standard practice in raising error.
        fprintf(stderr, "[matrix_get_element] (%i,%i) out of range. Exiting.",i,j);
        exit(EXIT_FAILURE);
    };
    
    return mat->elements[mat->cols*i + j];
}

void vector_print (vector_t* vec, char* name) {
    int i;

    printf("%s <%zu> : [\n",name,vec->length);
    for (i=0;i<vec->length;i++) {
        printf("  %f,\n",vec->elements[i]);
    };
    printf("]\n");
}

void matrix_print (matrix_t* mat, char* name) {
    printf("%s <%zu,%zu>: [\n",name,mat->rows,mat->cols);
    for (int i = 0; i < mat->rows; i++) {
        for (int j = 0; j < mat->cols; j++) {
            printf("  %f,\t",matrix_get_element(mat,i,j));
        }
        printf("\n");
    }
    printf("]\n");

}

void matrix_vector_multiply (vector_t* res, matrix_t *mat, vector_t* vec) {
    if (mat->rows != vec->length) {
        fprintf(stderr,"mat rows != vector len! (%zu!=%zu)", mat->rows, vec->length);
        exit(EXIT_FAILURE);
    };

    int i,j;
    for (i = 0;i < res->length;i++) {
        res->elements[i] = 0.;
        for (j = 0;j < vec->length;j++) {
            res->elements[i] += vec->elements[j] * matrix_get_element(mat, i, j);
            //printf("[%f,%f]\n",vec->elements[j],matrix_get_element(mat, i, j));
        };
    };
};

void vector_add (vector_t* res, vector_t* veca, vector_t* vecb) {

    if (veca->length != vecb->length) {
        fprintf(stderr,"vector length mismatch (%zu!=%zu)",veca->length,vecb->length);
        exit(EXIT_FAILURE);
    }

    for (int i=0; i<veca->length; i++) {
        res->elements[i] = veca->elements[i] + vecb->elements[i];
    }

}

void sim_step (vector_t* next_state, matrix_t* update, vector_t* state, vector_t* force) {
    matrix_vector_multiply(next_state,update,state);
    vector_add(state,next_state,force);
    //vector_print(state,"State");
}

void matrix_place_vector (matrix_t* mat, vector_t* vec, int index) {
    
    if (mat->cols != vec->length) {
        fprintf(stderr,"mat cols != vector len! (%zu!=%zu)", mat->rows, vec->length);
        exit(EXIT_FAILURE);
    };

    for (int j=0; j < vec->length; j++) {
        mat->elements[index*mat->cols + j] = vec->elements[j];
    }
    
}

int main(void) {
    matrix_t update_matrix;
    vector_t force_vector;
    float dt=1e-3;
    float g=9.81;
    
    //float stop_time = 10; //seconds
    int num_steps = 500; 
    printf("Number of steps: %i\n",num_steps);
    if (num_steps > 1000) {
        printf("Warning: simulating more than 1000 steps.\n");
    }

    matrix_t result_matrix;
    float result_matrix_elements[num_steps*4];
    result_matrix.cols = 4;
    result_matrix.rows = num_steps;
    result_matrix.elements = result_matrix_elements;
        
    vector_t state;
    float state_elements[4] = {
        0.,
        0.,
        1.,
        1.
    };
    state.length = 4;
    state.elements = state_elements;

    float update_matrix_elements[4*4] = {
        1,  0,  dt,  0 ,
        0,  1,  0 ,  dt,
        0,  0,  1 ,  0 ,
        0,  0,  0 ,  1 ,
    };
    update_matrix.rows = 4;
    update_matrix.cols = 4;
    update_matrix.elements = update_matrix_elements;

    float force_vector_elements[4] = {
        0,
        0,
        0,
        -g*dt
    };
    force_vector.length = 4;
    force_vector.elements = force_vector_elements;

    matrix_print(&update_matrix, "Update Matrix");
    vector_print(&force_vector, "Force Vector");
    vector_print(&state,"Initial State");

    vector_t next_state;
    float next_state_elements[4];
    next_state.elements = next_state_elements;
    next_state.length = 4;

    for (int step=0;step<num_steps;step++) {
        sim_step(&next_state,&update_matrix,&state,&force_vector);
        matrix_place_vector(&result_matrix,&state,step);
    }

    matrix_print(&result_matrix,"Results");

};
```

>[!tip] Results
>Forward Euler always seems to overshoot the analytical solution. This is likely because we *reduce the velocity over time, but we calculate the change in position with the previous velocity.*
>
>So then, $x_{n+1}=x_n+\Delta t v_n$.

# Plotting

Plan: let's just pass the matrix to matplotlib. An interactive plotting framework is nice to implement, but that's not what we're doing right now.

I implemented a pass between C and Python

```c
// Nearly a general array
int tensor_write_bin (const char* filename, const Matrix* mat) {

    FILE* file = fopen(filename,"wb");
    if (!file) {
        fprintf(stderr, "Failed to open file.");
        return 1;
    }
    
    // Start file with ndims
    size_t ndims = 1;
    fwrite(&ndims, sizeof(size_t), 1, file);

    // File starts with rows and cols
    fwrite(&mat->rows, sizeof(size_t), 1, file);
    fwrite(&mat->cols, sizeof(size_t), 1, file);

    // Then, the payload
    size_t matBufferLength = mat->rows*mat->cols;
    fwrite(mat->elements, sizeof(float), matBufferLength, file);

    return 0;
}
```

```python
def read_array_bin(filename):

    size_t = ctypes.sizeof(ctypes.c_size_t);

    if size_t == 4:
        datatype = np.uint32;
    else:
        datatype = np.uint64;

    with open(filename,'rb') as f:
        ndims = np.fromfile(f,datatype,1)[0];
        shape = np.fromfile(f,datatype,ndims); 
        array = np.fromfile(f,np.float32,1000);
    
    return array.reshape(shape)
```

Then we use the matplotlib animations library to animate it:

```python
    res_array = read_array_bin(args.input_file)
    print(res_array)

    x_pos = res_array[0]
    y_pos = res_array[1]

    fig, ax = plt.subplots()
    line = ax.plot(x_pos[0], y_pos[0], label=f'Trajectory')[0]
    
    ax.set(xlim=[0,20],ylim=[-5.5,5.5],xlabel='x', ylabel='y')
    ax.legend()

    def update(frame):
        x = x_pos[:frame]
        y = y_pos[:frame]
        line.set_xdata(x)
        line.set_ydata(y)
        return (line,line)

    dt = 5e-3
    frames = res_array.shape[1] # Total number of frames
    interval = dt # Delay between frames

    ani = animation.FuncAnimation(fig=fig, func=update, frames=frames, interval=dt)
    plt.show()

    fps = int(1/dt)
    ani.save(f'{filename}.gif',fps=60)
```

![Trajectory without drag](attachments/forwardEuler.gif)

# Forward Euler with Quadratic Drag

The quadratic drag equation has (mostly) no analytical solutions.

With drag, a force proportional to the square of the velocity develops opposing the direction of the velocity:
$$\vec{F}=-k|\vec{v}|\vec{v}$$
The update matrix turns into:
$$\mathbf{U}=\begin{bmatrix}
1 & 0 & dt & 0 \\
0 & 1 & 0 & dt \\
0 & 0 & 1-k|v| & 0 \\
0 & 0 & 0 & 1-k|v| \\
\end{bmatrix}, \vec{F}=\begin{bmatrix}
0 \\ 0 \\ 0 \\ -g\cdot dt
\end{bmatrix}$$

To implement drag, we also update the update matrix every time step:

```c
void get_update_matrix (Matrix* upd,const Vector* state,const float dt, const float drag_constant) {

    float x = state->elements[0];
    float y = state->elements[1];
    float vx = state->elements[2];
    float vy = state->elements[3];

    float speed = sqrtf(vx*vx + vy*vy); 
    float drag = speed*drag_constant;

    float updated_elements[4*4] = {
        1,  0,  dt     ,  0      ,
        0,  1,  0      ,  dt     ,
        0,  0,  1-drag ,  0      ,
        0,  0,  0      ,  1-drag ,
    };

    memcpy(upd->elements, updated_elements, sizeof(updated_elements));

}
```

![Forward Euler with Drag](attachments/forwardEuler%202.gif)

Notice that with quadratic drag, the system is now nonlinear and the "update matrix" no longer makes sense (it's a function of the state vector it's operating on, so it's not linear). We can replace the matrix stuff with a generic update of the state:

```c
void sim_step (Vector* state,const Vector* force, const float dt, const float drag_per_mass) {

    float x = state->elements[0];
    float y = state->elements[1];
    float vx = state->elements[2];
    float vy = state->elements[3];

    float speed = sqrtf(vx*vx + vy*vy);

    float dx = vx;
    float dy = vy;
    float dvx = vx*(-speed*drag_per_mass) + force->elements[2];
    float dvy = vy*(-speed*drag_per_mass) + force->elements[3];
    
    state->elements[0] = x + dt*dx;
    state->elements[1] = y + dt*dy;
    state->elements[2] = vx + dt*dvx;
    state->elements[3] = vy + dt*dvy;

}
```


# Runge-Kutta 4

Forward euler is technically RK1. The 4 means we approximate the correct average slope over the time step with 4 different estimates.

>[!tip] [Runge-Kutta](https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods)
>Given a problem in the following form: 
>$$\frac{dy}{dt}=f(t,y), y(t_0)=y_0$$
>RK4 gives an estimate of $\frac{dy}{dt}$ using a weighted average of four slopes $f(t,y)$ $k_1$ to $k_4$ in the "future" of the current point in time
>Choosing a time step $\Delta t>0$
>$$y_{n+1}=y_n+\frac{\Delta t}{6}(k_1+2k_2+2k_3+k_4)$$
>$$t_{n+1}=t_n+\Delta t$$
>$$k_1=f(t_n,y_n),$$
>$$k_2=f(t_n+\frac{\Delta t}{2},y_n+\Delta t\frac{k_1}{2})$$
>$$k_3=f(t_n+\frac{\Delta t}{2},y_n+\Delta t\frac{k_2}{2})$$
>$$k_4=f(t_n+\Delta t,y_n+\Delta tk_3)$$

If the forward euler equation for $v_y$ is
$$v_{y,t+1}=f(t_n,v_y)=v_{y,t} -g\Delta t-k|\vec{v}|v_{y,t}$$
Then the RK4 estimates would be
$$k_1=v_{y,t} (1-k|\vec{v}|) -g\Delta t$$
$$k_2=(v_{y,t}+\frac{\Delta tk_1}{2}) (1-k|\vec{v}(\frac{\Delta tk_1}{2})|) -g\frac{3\Delta t}{2}$$
$$k_3=(v_{y,t}+\frac{\Delta tk_2}{2}) (1-k|\vec{v}(\frac{\Delta tk_2}{2})|) -g\frac{3\Delta t}{2}$$
$$k_4=(v_{y,t}+\Delta tk_3) (1-k|\vec{v}(\Delta tk_3)|) -g2\Delta t$$
# RK4 implementation

The most important part of the RK4 implementation has to be the `get_slope` function refactor
```c
void get_slope(const Vector* slope,Vector* state,const Vector* force, const float drag_per_mass) {

    float vx = state->elements[2];
    float vy = state->elements[3];

    float speed = sqrtf(vx*vx + vy*vy);

    slope->elements[0] = vx;
    slope->elements[1] = vy;
    slope->elements[2] = vx*(-speed*drag_per_mass) + force->elements[2];
    slope->elements[3] = vy*(-speed*drag_per_mass) + force->elements[3];
}
```

and the accompanying changes in the way we step the simulation

```c
void sim_step(Vector* state,const Vector* force, const float dt, const float drag_per_mass) {

    Vector slope = {
        .elements = (float[4]){},
        .length = 4
    };

    get_slope(&slope, state, force, drag_per_mass);
    vector_scalar_multiply(dt, &slope);
    vector_add(state, state, &slope);
}

```

with this, it's easy to add RK4 by just chaining the calls to `get_slope` in order to use previous RK estimates for the next ones.

```c
    get_slope(&k1, state, force, drag_per_mass);

    vector_scalar_multiply_copy(&scratch,0.5*dt, &k1);
    vector_add(&scratch, state, &scratch); // State + 0.5*dt*k1;
    get_slope(&k2, &scratch, force, drag_per_mass);

    vector_scalar_multiply_copy(&scratch,0.5*dt, &k2);
    vector_add(&scratch, state, &scratch); // State + 0.5*dt*k2;
    get_slope(&k3, &scratch, force, drag_per_mass);

    vector_scalar_multiply_copy(&scratch,dt, &k3);
    vector_add(&scratch, state, &scratch); // State + dt*k3;
    get_slope(&k4, &scratch, force, drag_per_mass);

    vector_scalar_multiply(2,&k2);
    vector_scalar_multiply(2,&k3);
    vector_add(&slope, &k1, &k2);
    vector_add(&slope, &slope, &k3);
    vector_add(&slope, &slope, &k4);

    vector_scalar_multiply(dt/6, &slope);
    vector_add(state, state, &slope);

```

Here's the comparison of RK4 with a refactored and better version of the forwardEuler.

>[!note]
>More specifically, in the new forwardEuler the drag constant doesn't include `dt` in it by accident, and it's easier to track its effect.
>
>This had to be done so that we can see how the sims behave with the same drag coefficient.

![](attachments/trajectories.gif)

We were promised that RK4 follows the real thing better, and it does here. 

We know from the initial sims that Forward Euler tends to overshoot when all you do is reduce the velocity (which is what drag and gravity does). Here, we see that RK4 undershoots the Euler estimate- which means it doesn't have the same overshoot.