from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - dropout: Scalar between 0 and 1 giving dropout strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian with standard deviation equal to   #
        # weight_scale, and biases should be initialized to zero. All weights and  #
        # biases should be stored in the dictionary self.params, with first layer  #
        # weights and biases using the keys 'W1' and 'b1' and second layer weights #
        # and biases using the keys 'W2' and 'b2'.                                 #
        ############################################################################
        W1 = weight_scale * np.random.randn(input_dim, hidden_dim)
        b1 = np.zeros(hidden_dim)
        W2 = weight_scale * np.random.randn (hidden_dim, num_classes)
        b2 = np.zeros (num_classes)
        self.params.update({
            'W1': W1,
            'b1': b1,
            'W2': W2,
            'b2': b2
        })
        pass
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################


    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        fc1, cache_fc1 = affine_forward (X, self.params['W1'], self.params['b1'])
        reLU, cache_reLU = relu_forward(fc1)
        scores, cache_scores = affine_forward (reLU, self.params['W2'], self.params['b2'])
        pass
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        probs = np.exp(scores) / np.sum (np.exp(scores), axis = 1, keepdims = True)
        correct_probs = probs[range(X.shape[0]), y]
        data_loss  = np.sum (-np.log (correct_probs) ) / X.shape[0]
        reg_loss = 0.5 * self.reg *(  np.sum (self.params['W1'] ** 2) + np.sum (self.params['W2'] ** 2))
        loss = data_loss + reg_loss

        dscores = probs
        dscores [range(X.shape[0]), y] -= 1
        dscores /= X.shape[0]        
        dreLU, dW2, db2 = affine_backward (dscores, cache_scores)
        dW2 += self.reg * self.params['W2']
        dreLU_back = relu_backward (dreLU, cache_reLU)
        dX, dW1, db1 = affine_backward(dreLU_back,  cache_fc1)
        dW1 += self.reg * self.params['W1']
        grads.update ({
            'W1': dW1,
            'b1': db1,
            'W2': dW2,
            'b2': db2
        })
        pass
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=0, use_batchnorm=False, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=0 then
          the network should not use dropout at all.
        - use_batchnorm: Whether or not the network should use batch normalization.
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.use_batchnorm = use_batchnorm
        self.use_dropout = dropout > 0
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution with standard deviation equal to  #
        # weight_scale and biases should be initialized to zero.                   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to one and shift      #
        # parameters should be initialized to zero.                                #
        ############################################################################
        #init without batch normalization
        if type(hidden_dims) != list:   
            raise ValueError('hidden_dims has to be a list')
        
        h_dims = [input_dim] + hidden_dims + [num_classes]
        num_weight = len(hidden_dims) +1
        b = {'b' + str(i +1):  np.zeros (h_dims[i+ 1] )  for i in range (num_weight) }
        W = {'W' + str(i+1): weight_scale * np.random.randn (h_dims[i], h_dims[i+1]) for i in range (num_weight)}
        self.params.update(b)
        self.params.update (W)
        #init with batch normalization
        if self.use_batchnorm : 
            gamma = {'gamma' + str(i+1) : np.ones(h_dims[i+1]) for i in range (num_weight -1 )} #the last weight layer, no batchnorm layer
            beta =  {'beta' + str(i+1) : np.zeros (h_dims[i+1]) for i in range (num_weight - 1)}
            self.params.update(gamma)
            self.params.update (beta)
        pass
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.use_batchnorm:
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)


    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.use_batchnorm:
            for bn_param in self.bn_params:
                bn_param['mode'] = mode #change all bn_params according to the loss param y

        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        layers =[]
        relu_layers = []
        bn_layers = []
        cache_relu_layers = []
        cache_layers = []
        cache_bn_layers = []
        num_weight = self.num_layers
        for i in range(num_weight):
            #first layer, input: X
            if i == 0:
                t_a , t_b = affine_forward (X, self.params['W1'], self.params['b1'])
                layers.append(t_a)
                cache_layers.append(t_b) 
            #not first layer, input is the last reLU result
            else:
                t_c, t_d = affine_forward (relu_layers[i-1], self.params['W'+str(i+1)], self.params['b' + str(i+1)])
                layers.append(t_c)
                cache_layers.append(t_d)
            #bn_layer before reLU layers
            if i is not num_weight -1:
                bn_a , bn_b = batchnorm_forward(layers[i], self.params['gamma' + str(i+1)], \
                                                        self.params['beta' + str(i+1)], self.bn_params[i])
                bn_layers.append(bn_a)
                cache_bn_layers.append(bn_b)
                t_e, t_f = relu_forward(bn_layers[i])
                relu_layers.append(t_e) 
                cache_relu_layers.append(t_f)
            else:
                t_e, t_f = relu_forward(layers[i])
                relu_layers.append(t_e) 
                cache_relu_layers.append(t_f)
        #Finally, relu_layers, layers share shape[0], 1 bigger than bn_layer's
        #scores are last layer's output, it should not go through reLU or bn_layer
        scores = layers[-1]  
        num_example = X.shape[0]
        pass
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        probs = np.exp(scores) / np.sum (np.exp(scores), axis = 1, keepdims = True)
        correct_probs = probs[range(num_example), y]
        data_loss  = np.sum (-np.log (correct_probs) ) / num_example
        reg_loss = 0.5 * self.reg *(  np.sum ( [ np. sum (self.params['W' + str(i+1)] ** 2 )  for i in range (num_weight)  ] ) )
        loss = data_loss + reg_loss

        dscores = probs
        dscores [range(num_example), y] -= 1
        dscores /= num_example

        dreLU = []
        dreLU_back = []
        dW = []
        db = []
        dgamma = []
        dbeta = []
        dx = []
        #all input should be from reLU, the first one USED should be equal to dscores
        for i in range(num_weight):
            if i == 0:
                dreLU = [dscores] + dreLU
                dreLU_back = [ dscores ] + dreLU_back
                #there is no bn_layer or reLU layer at the very end
                dx_ , dw_, db_ = affine_backward (dreLU_back[0], cache_layers[num_weight - i -1])
            else:
                dreLU_back = [relu_backward(dreLU[0] , cache_layers[num_weight -i -1])] + dreLU_back
                dxx_, dgamma_, dbeta_ = batchnorm_backward(dreLU_back[0], cache_bn_layers[num_weight -i - 1])
                dx = [dxx_] + dx
                dgamma = [dgamma_] + dgamma
                dbeta = [dbeta_ ] + dbeta
                dx_ , dw_, db_ = affine_backward (dx[0], cache_layers[num_weight - i -1])
            dW = [  dw_ + self.reg * cache_layers[num_weight - i -1][1] ] + dW
            db = [  db_ ]+ db
            dreLU =[  dx_  ] + dreLU
        _dW = { 'W'+str(i+1): dW[i]  for i in range (num_weight) }
        _db = {'b' + str(i+1): db[i] for i in range (num_weight)}
        _dgamma = {'gamma' + str(i+1): dgamma[i] for i in range (num_weight -1)}
        _dbeta =  {'beta' + str(i+1): dbeta[i] for i in range (num_weight - 1)}
        grads.update(_dW)
        grads.update(_db)
        grads.update (_dgamma)
        grads.update (_dbeta)
        pass
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads
