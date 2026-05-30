# Create New Questions from an Inspirational Source

You are a teacher, and you want to create a new set of practice exercises for your students so that they will not feel bored doing the same homework, exercises over and over. Also, the creation of new exercises will help you broaden your view in learning, teaching, and exploring mathematics.

## 0.1 Copyright criteria

Clearly, you must base on some sources and you want to avoid potential copyright issues. The following criteria should help you to do that.
* Change the context of the question completely or as much as possible.
* Avoid using the same formulas, constants, or symbols as the source. Only keep the main idea to solve the problem. For example, if the question involves $\sin x$, change it into another appropriate trigonometric function.
* Your question and the inspirational source should not contain more than 5 common words, excluding the mathematical terms and conjunctions.
* Your question and the inspirational source should not contain more than 3 consecutive common words, excluding the mathematical terms and conjunctions.
* In any case, keep the main idea of how to solve the problem.

## 0.2 How to create a new exercise

With the above criteria, how can we create a new exercise? Here is a step-by-step guide.
1. Solve the source exercise. Find the key ideas of the solution.
2. Find the parameters in the source exercise that could be changed. The more you find; the more creative your new exercise will be.
3. Find the new context for your new question based on the key ideas of the solution.
    * For example, if the source involves linear motion in physics, like $s = s_0 + vt$, you should find another application that involves linear equation in physics, such as the increase of pressure with respect to depth.
    * You should use AI tools to create new contexts. A prompt like this: Given the source exercise involving linear motion..., find a new application of linear equations in physics and create a similar exercise could help you.
4. Apply the generalization in step 2 to the result you obtain in step 3.
5. Check the newly created question with respect to the rule above.

---

## 1 Examples

### 1.1 Computational examples

**Example 1**
**Source:** For the limit $\lim_{x \to 0} \frac{e^{2x} - 1}{2x} = 1$, illustrate Definition 2 by finding values of $\delta$ that correspond to $\epsilon = 0.5$ and $\epsilon = 0.1$.
**A not really good version:** Suppose you want to prove that $\lim_{x \to 0} \frac{e^{3x} - 1}{3x} = 1$ using the precise definition of a limit. You first let $\epsilon > 0$ and then choose a value $\delta = \min\{1, \delta_1(\epsilon)\}$ where $\delta_1$ is a function of $\epsilon$. Which of the following represents a possible expression for $\delta_1$?
**A recommended version:** Elucidate $\lim_{x \to 0} \frac{e^{3x} - 1}{3x} = 1$ by choosing appropriate $\delta$ as a function of $\epsilon$ in the precise definition of a limit.

**Example 2**
**Source:** How close to $-3$ do we have to take $x$ so that $\frac{1}{(x + 3)^4} > 10000$?
**A not really good version:** How closely must $x$ approach $-3$ so that $\frac{1}{(x + 3)^4} > 10000$?
**A recommended version:** Find the maximal value of $\delta$ such that $\frac{1}{(x + 8)^2} > 64$ for all $x \in (8 - \delta, 8 + \delta)$.

**Example 3**
**Source:** If $c > \frac{1}{2}$, how many lines through the point $(0, c)$ are normal lines to the parabola $y^2 = x$? What if $c < \frac{1}{2}$?
**A not really good version:** You are given the point $(0, c)$ on the Cartesian coordinate plane. Determine how many distinct normals to the parabola $y^2 = 3x$ pass through this point when: (a) $c > \frac{1}{6}$ (b) $c \le \frac{1}{6}$.
**A recommended version:** Let $y^2 = 3x$. Find the number of distinct normal lines to the parabola that pass through the point $(0, c)$ when: (a) $c > \frac{1}{6}$ (b) $c \le \frac{1}{6}$.

**Example 4**
**Source:** The equation $y'' + y' - 2y = x$ is called a differential equation because it involves an unknown function $y$ and its derivatives $y', y''$. Find constants $A, B, C$ such that the function satisfies this equation.
**A not really good version:** The equation $y'' + y' - 2y = x$ is classified as a differential equation because it includes a function $y$ and its first and second derivatives. Determine the constants $A, B, C$ so that the function $y = Ax^2 + Bx + C$ satisfies this equation.
**A recommended version:** A differential equation is an equation involving an unknown function and its derivatives. Find constants $A, B, C$ such that $y = Ax^2 + Bx + C$ is a solution of $y'' + y' - 2y = \sin x$.

### 1.2 Application examples

**Example 5**
**Source:** A Norman window has the shape of a rectangle surmounted by a semicircle. If the perimeter of the window is 30 ft, express the area $A$ of the window as a function of the width $x$ of the window.
**A not really good version:** A Norman window consists of a rectangular section topped by a semicircular arch. Given that the perimeter of this window measures 46 ft, find the area of this window, denoted $A$, in terms of its width $x$.
**A recommended version:** A city park features a decorative garden plot shaped like a rectangular section topped by a semicircular arch. The total perimeter enclosing the garden is 29 ft. Determine the area $A$ of the garden in terms of its width $x$.

**Example 6**
**Source:** Recent studies indicate that the average surface temperature of the earth has been rising steadily. Some scientists have modeled the temperature by the linear function $T = 0.01t + 10$, where $T$ is the temperature in $F$ and $t$ represents years since 2000.
a. What do the slope and $T$-intercept represent?
b. Use the equation to predict the earth's average surface temperature in 3000?
**A not really good version:** Scientists have proposed a linear model to represent the rise in Jupiter's average surface temperature over time. The model is given by $T = 0.04t + 10$ where $T$ is the temperature in $F$ and $t$ represents years since 1990.
a. Find the slope and the $T$-intercept of the equation, and identify their real-world implications.
b. Using this model, estimate Jupiter's average surface temperature in the year 2064?
**A recommended version:** The pressure an exploration vessel experiences in an ocean on Neptune increases at a constant rate as it descends. This relationship can be modeled by the linear function: $P(h) = 11.1826h + 100$ where $P$ is the total pressure in kilopascals (kPa), and $h$ is the depth in meters below the surface of the ocean.
a. Find the slope and the $P$-intercept of the equation. What best describes the real implications of the slope and the y-intercept?
b. Use the equation to calculate the total pressure on a diver at a depth of 74 meters.
c. The pressure at some level of depth is 456. Find the depth.
