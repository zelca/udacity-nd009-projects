import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.action = None
        self.reward = None
        self.q = self.init_q()

    def reset(self, destination=None):
        self.planner.route_to(destination)
        self.state = None
        self.action = None
        self.reward = None

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # Get new state
        new_state = (self.next_waypoint, inputs["light"], inputs["oncoming"], inputs["left"])

        # Learn policy based on state, action, reward
        if self.state:
            self.update_q(self.state, self.action, self.reward, new_state)

        # Update state
        self.state = new_state

        # Select action according to your policy
        self.action, _ = self.get_action(self.state)

        # Execute action and get reward
        self.reward = self.env.act(self, self.action)

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, waypoint={}, reward = {}" \
            .format(deadline, inputs, self.action, self.next_waypoint, self.reward)  # [debug]

    def init_q(self):
        q = {}
        init_q = .1
        for waypoint in self.env.valid_actions:
            for light in ['green', 'red']:
                for oncoming in self.env.valid_actions:
                    for left in self.env.valid_actions:
                        init_actions = {}
                        for action in self.env.valid_actions:
                            init_actions[action] = init_q
                        q[(waypoint, light, oncoming, left)] = init_actions
        return q

    def update_q(self, state, action, reward, new_state):
        learning_rate = 1  # environment is completely deterministic
        discount_factor = 0  # environment is completely deterministic
        q = self.q[state][action]
        _, max_q = self.get_action(new_state)
        new_q = q + learning_rate * (reward + discount_factor * max_q - q)
        #print "{} old q {} new q {}".format(state, q, new_q)
        self.q[state][action] = new_q

    def get_action(self, state):
        max_q = None
        max_action = None
        for action, q in self.q[state].iteritems():
            if q > max_q:
                max_q = q
                max_action = action
        #print "action - {} ({})".format(max_action, max_q)
        return max_action, max_q


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.1, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
