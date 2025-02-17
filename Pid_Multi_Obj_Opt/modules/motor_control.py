import control as ctrl
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import simpson

class DCMotorTransferFunction:
    """Represents a transfer function model of a DC Motor.

    Attributes:
        kt (float): Torque constant.
        kb (float): Back EMF constant.
        J (float): Moment of inertia of the rotor (kg*m^2).
        L (float): Inductance (H).
        b (float): Damping ratio of the mechanical system (Nm/s).
        R (float): Resistance (Ω).
        motor_tf (ctrl.TransferFunction): The motor's transfer function.
    """

    def __init__(self, kt, kb, J, L, b, R) -> None:
        """Initializes the DC Motor with given parameters and computes its transfer function."""
        self.kt = kt  # Torque constant
        self.kb = kb  # Back EMF constant
        self.J = J  # Moment of inertia of the rotor (kg*m^2)
        self.L = L  # Inductance (H)
        self.b = b  # Damping ratio of the mechanical system (Nm/s)
        self.R = R  # Resistance (Ω)
        
        num = [self.kt]
        den = [self.J*self.L, self.J*self.R + self.L*self.b, self.b*self.R + self.kt*self.kb]
        self.motor_tf = ctrl.TransferFunction(num, den)

    def get_transfer_function(self):
        """Returns the motor's transfer function."""
        return self.motor_tf
    
    def __call__(self) -> ctrl.TransferFunction:
        """Allows the class instance to be called as a function, returning the transfer function."""
        return self.motor_tf

class PIDTransferFunction:
    """Represents a PID controller's transfer function.

    Attributes:
        kp (float): Proportional gain.
        ki (float): Integral gain.
        kd (float): Derivative gain.
        pid_tf (ctrl.TransferFunction): The PID controller's transfer function.
    """
    
    def __init__(self, kp=1, ki=0, kd=0) -> None:
        """Initializes the PID controller with given parameters."""
        self.set_pid(kp=kp, ki=ki, kd=kd)

    def set_pid(self, kp, ki, kd):
        """Sets the PID parameters and updates the controller's transfer function."""
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        num = [self.kd, self.kp, self.ki]
        den = [1, 0]
        self.pid_tf = ctrl.TransferFunction(num, den)
        
    def get_transfer_function(self):
        """Returns the PID controller's transfer function."""
        return self.pid_tf
    
    def __call__(self) -> ctrl.TransferFunction:
        """Allows the class instance to be called as a function, returning the transfer function."""
        return self.pid_tf

class MotorResponse:
    """Manages simulation and visualization of motor responses to control inputs.
    
    Attributes:
        t (np.ndarray): Time vector for simulation.
    """
    
    def __init__(self, t) -> None:
        """Initializes the response simulator with a time vector."""
        self.t = t

    def open_loop_step_response(self, sys, C=1, v_in=1, start_from=0, viz=False):
        """Simulates and optionally visualizes the open-loop step response of a system.

        Args:
            sys (ctrl.TransferFunction): The system's transfer function.
            C (float): Constant multiplier for the system, default is 1.
            v_in (float): Step input voltage, default is 1V.
            start_from (float): Time to start the step input, default is 0 seconds.
            viz (bool): Whether to visualize the response, default is False.

        Returns:
            tuple: Time vector and response of the system.
        """
        # Create the step input with delayed start
        step_input = np.zeros_like(self.t)
        step_input[self.t >= start_from] = v_in

        # Simulate step response
        t, response = ctrl.forced_response(sys*C, T=self.t, U=step_input)
        info = 1# ctrl.step_info(v_in*sys*C, T=self.t)
        
        if viz:
            # Visualization
            plt.figure(figsize=(10, 6))
            plt.plot(t, step_input, 'r--', label=f'Input Step ({v_in}V starting at {start_from}s)')
            plt.plot(t, response, 'b-', label='Motor Response')
            plt.title(f'Step Response with Delayed {v_in}V Step Input')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Response')
            plt.legend(loc='best')
            plt.grid(True)
            plt.show()

        return t, response, info
    
    def close_loop_step_response(self, sys, C, v_desired, start_from=0, show=False, save=False, info=False, c_coeff=None):
        """Simulates and optionally visualizes the closed-loop step response of a system.

        Args:
            sys (ctrl.TransferFunction): The system's transfer function.
            C (ctrl.TransferFunction): The controller's transfer function.
            v_desired (float): Desired step input value.
            start_from (float): Time to start the step input, default is 0 seconds.
            viz (bool): Whether to visualize the response and error, default is False.

        Returns:
            tuple: Time vector, system response, and error array.
        """
        # Setup closed-loop system
        system_open_loop = ctrl.series(C, sys)
        system_closed_loop = ctrl.feedback(system_open_loop, 1)

        # Desired step input
        step_input = np.zeros_like(self.t)
        step_input[self.t >= start_from] = v_desired

        # Simulate response
        t, response = ctrl.forced_response(system_closed_loop, T=self.t, U=step_input)

        step_info = None
        if info:
            step_info = ctrl.step_info(v_desired*system_closed_loop, T=self.t)

        # Calculate error
        error = step_input - response
        
        if show:
            # Visualization
            fig = plt.figure(figsize=(12, 8))
            if info:
                fig.suptitle(f"Response with controller kp={np.round(c_coeff[0],2)},ki={np.round(c_coeff[1],2)},kd={np.round(c_coeff[2],2)},  \nRiseTime: {np.round(step_info['RiseTime'],4)}[sec] | OverShoot: {np.round(step_info['Overshoot'],3)}[%]")
            
            ax = fig.add_subplot(2,1,1)
            ax.plot(t, step_input, 'r--', label=f'Desired Value ({v_desired})')
            ax.plot(t, response, 'b-', label='System Response')

            ax.set_title('Closed-loop Response and Error')
            ax.set_ylabel('Response')
            ax.legend(loc='best')
            ax.grid(True)

            ax2 = fig.add_subplot(2,1,2)
            ax2.plot(t, error, 'g-', label='Error')
            ax2.set_xlabel('Time (seconds)')
            ax2.set_ylabel('Error')
            ax2.legend(loc='best')
            ax2.grid(True)
            plt.show()
        
        if save:
            fig.savefig(f"figures/response_kp{int(c_coeff[0])}_ki{int(c_coeff[1])}_kd{int(c_coeff[2])}")

        return t, response, error, step_info
    
class Criterion:
    """Defines and computes performance criteria based on error and time vectors.

    Attributes:
        name (str): The name of the performance criterion.
        function (function): The lambda function implementing the criterion calculation.
    """
    
    def __init__(self, name):
        """Initializes the Criterion object with a given performance criterion name."""
        self.name = name.upper()
        self.function = self._get_criterion_function()

    def _get_criterion_function(self):
        """Determines and returns the appropriate lambda function for the specified criterion."""
        if self.name == 'ISE':
            return lambda e, t: simpson(y=e**2, x=t)
        elif self.name == 'IAE':
            return lambda e, t: simpson(y=np.abs(e), x=t)
        elif self.name == 'ITAE':
            return lambda e, t: simpson(y=t * np.abs(e), x=t)
        elif self.name == 'ITSE':
            return lambda e, t: simpson(y=t * e**2, x=t)
        else:
            raise ValueError("Invalid criterion name. Please use 'ISE', 'IAE', 'ITAE', or 'ITSE'.")

    def __call__(self, e, t):
        """Computes the criterion based on provided error and time vectors.

        Args:
            e (np.ndarray): Error array.
            t (np.ndarray): Time vector.

        Returns:
            float: The computed performance criterion.
        """
        return self.function(e, t)


def example():
    motor_tf = DCMotorTransferFunction(kt=0.01,
                                        kb=0.01,
                                        J=0.01,
                                        L=0.5,
                                        b=0.1,
                                        R=1)
    sys = motor_tf.get_transfer_function()
    
    C_pid = PIDTransferFunction(kp=200,ki=100,kd=10)
    C = C_pid.get_transfer_function()
    
    t = np.linspace(0, 2, 1000)  # Time from 0 to 10 seconds
    
    response = MotorResponse(t=t)
    
    t, res, info = response.open_loop_step_response(sys=sys,
                                            viz=True)
    
    t,res,e, info = response.close_loop_step_response(sys = sys,
                                                C=C,
                                                v_desired=2,
                                                start_from=1,
                                                viz=True)
    
    ISE = Criterion("ISE")
    IAE = Criterion("IAE")
    ITAE = Criterion("ITAE")
    ITSE = Criterion("ITSE")
    
    print("PID performance criterions: ")
    print(f"ISE: {ISE(e,t)} | IAE: {IAE(e,t)} | ITAE: {ITAE(e,t)} | ITSE: {ITSE(e,t)} ")

if __name__ == "__main__":
    example()