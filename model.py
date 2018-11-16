import tensorflow as tf
import numpy as np

class QNetworkTf():
    """Actor (Policy) Model."""

    def __init__(self, session, state_size, action_size, name):
        """Initialize parameters and build model.
        Params
        ======
            state_size (int): Dimension of each state
            action_size (int): Dimension of each action
            seed (int): Random seed
        """
        self.sess = session
        self.name = name

        self.input = tf.placeholder(tf.float32, shape=(None, state_size))
        self.y_input = tf.placeholder(tf.float32, shape=(None, 1))
        self.loss_modifier = tf.placeholder(tf.float32, shape=(None))

        self.gather_index = tf.placeholder(tf.int32, shape=(None))

        self.output = self._inference()
        self.loss, self.reduced_loss, self.optimizer = self._training_graph()

        self.train_writer = tf.summary.FileWriter('models/',
                                                  self.sess.graph)

        self.sess.run([tf.global_variables_initializer(),
                       tf.local_variables_initializer()])

        self.step = 0

    def _inference(self):
        with tf.variable_scope("inference_"+self.name):
            layer = tf.layers.dense(self.input, 64, activation=tf.nn.relu)
            layer = tf.layers.dense(layer, 64, activation=tf.nn.relu)
            layer = tf.layers.dense(layer, 4)
        return layer

    def _training_graph(self):
        with tf.variable_scope('training_'+self.name):
            pad = tf.range(tf.size(self.gather_index))
            pad = tf.expand_dims(pad, 1)
            ind = tf.concat([pad, self.gather_index], axis=1)

            gathered = tf.gather_nd(self.output, ind)
            gathered = tf.expand_dims(gathered, 1)
            loss = tf.losses.mean_squared_error(
                labels=self.y_input, predictions=gathered)
            loss = tf.multiply(self.loss_modifier, loss)
            reduced_loss = tf.reduce_mean(loss)

            optimize = tf.train.AdamOptimizer(
                learning_rate=5e-4).minimize(reduced_loss)


        return loss, reduced_loss, optimize

    def forward(self, state):
        """Build a network that maps state -> action values."""
        return self.sess.run(self.output, feed_dict={self.input: state})

    def train(self, states, y_correct, actions, modifier):
        ls, reduced, result, _ = self.sess.run([self.loss, self.reduced_loss, self.output, self.optimizer], feed_dict={
            self.input: states, self.y_input: y_correct, self.gather_index: actions, self.loss_modifier: modifier})
        return ls, reduced, result
