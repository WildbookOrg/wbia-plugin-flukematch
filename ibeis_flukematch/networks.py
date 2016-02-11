import lasagne.layers as ll
from lasagne.nonlinearities import linear, softmax, sigmoid, rectify
from lasagne.objectives import binary_crossentropy
from lasagne.updates import adam, nesterov_momentum
from lasagne.init import Orthogonal, Constant
from lasagne.regularization import l2, regularize_network_params
import theano.tensor as T
import theano



#----------- NOTCH TIPS EXTRACTOR

def build_kpextractor64():
    inp = ll.InputLayer(shape=(None, 1, 64, 64), name='input')
    # we're going to build something like what Daniel Nouri made for Facial Keypoint detection for a base reference
    # http://danielnouri.org/notes/2014/12/17/using-convolutional-neural-nets-to-detect-facial-keypoints-tutorial/
    # alternate pooling and conv layers to minimize parameters
    filter_pad = lambda x, y: (x//2, y//2)
    filter3 = (3, 3)
    same_pad3 = filter_pad(*filter3)
    conv1 = ll.Conv2DLayer(inp, num_filters=16, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv1')
    mp1 = ll.MaxPool2DLayer(conv1, 2, stride=2) # now down to 32 x 32
    bn1 = ll.BatchNormLayer(mp1)
    conv2 = ll.Conv2DLayer(bn1, num_filters=32, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv2')
    mp2 = ll.MaxPool2DLayer(conv2, 2, stride=2) # now down to 16 x 16
    bn2 = ll.BatchNormLayer(mp2)
    conv3 = ll.Conv2DLayer(bn2, num_filters=64, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv3')
    mp3 = ll.MaxPool2DLayer(conv3, 2, stride=2) # now down to 8 x 8
    bn3 = ll.BatchNormLayer(mp3)
    conv4 = ll.Conv2DLayer(bn3, num_filters=128, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv4')
    # larger max pool to reduce parameters in the FC layer
    mp4 = ll.MaxPool2DLayer(conv4, 2, stride=2) # now down to 4x4
    bn4 = ll.BatchNormLayer(mp4)
    conv5 = ll.Conv2DLayer(bn4, num_filters=256, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv5')
    mp5 = ll.MaxPool2DLayer(conv5, 2, stride=2) # down to 2x2
    bn5 = ll.BatchNormLayer(mp5)
    # now let's bring it down to a FC layer that takes in the 2x2x64 mp4 output
    fc1 = ll.DenseLayer(bn5, num_units=256, nonlinearity=rectify)
    bn6 = ll.BatchNormLayer(fc1)
    #dp1 = ll.DropoutLayer(bn1, p=0.5)
    fc2 = ll.DenseLayer(bn6, num_units=64, nonlinearity=rectify)
    #dp2 = ll.DropoutLayer(fc2, p=0.5)
    bn7 = ll.BatchNormLayer(fc2)
    out = ll.DenseLayer(bn7, num_units=6, nonlinearity=linear)
    out_rs = ll.ReshapeLayer(out, ([0], 3, 2))

    return out_rs

def build_kpextractor128():
    inp = ll.InputLayer(shape=(None, 1, 128, 128), name='input')
    # alternate pooling and conv layers to minimize parameters
    filter_pad = lambda x, y: (x//2, y//2)
    filter3 = (3, 3)
    same_pad3 = filter_pad(*filter3)
    conv1 = ll.Conv2DLayer(inp, num_filters=16, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv1')
    mp1 = ll.MaxPool2DLayer(conv1, 2, stride=2) # now down to 64 x 64
    bn1 = ll.BatchNormLayer(mp1)
    conv2 = ll.Conv2DLayer(bn1, num_filters=32, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv2')
    mp2 = ll.MaxPool2DLayer(conv2, 2, stride=2) # now down to 32 x 32
    bn2 = ll.BatchNormLayer(mp2)
    conv3 = ll.Conv2DLayer(bn2, num_filters=64, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv3')
    mp3 = ll.MaxPool2DLayer(conv3, 2, stride=2) # now down to 16 x 16
    bn3 = ll.BatchNormLayer(mp3)
    conv4 = ll.Conv2DLayer(bn3, num_filters=128, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv4')
    mp4 = ll.MaxPool2DLayer(conv4, 2, stride=2) # now down to 8 x 8
    bn4 = ll.BatchNormLayer(mp4)
    conv5 = ll.Conv2DLayer(bn4, num_filters=256, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv5')
    mp5 = ll.MaxPool2DLayer(conv5, 2, stride=2) # down to 4 x 4
    bn5 = ll.BatchNormLayer(mp5)

    conv6 = ll.Conv2DLayer(bn5, num_filters=512, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv6')
    mp6 = ll.MaxPool2DLayer(conv6, 2, stride=2) # down to 4 x 4
    bn6 = ll.BatchNormLayer(mp6)

    # now let's bring it down to a FC layer that takes in the 2x2x64 mp4 output
    fc1 = ll.DenseLayer(bn6, num_units=256, nonlinearity=rectify)
    bn1_fc = ll.BatchNormLayer(fc1)
    #dp1 = ll.DropoutLayer(bn1, p=0.5)
    fc2 = ll.DenseLayer(bn1_fc, num_units=64, nonlinearity=rectify)
    #dp2 = ll.DropoutLayer(fc2, p=0.5)
    bn2_fc = ll.BatchNormLayer(fc2)
    out = ll.DenseLayer(bn2_fc, num_units=6, nonlinearity=linear)
    out_rs = ll.ReshapeLayer(out, ([0], 3, 2))

    return out_rs


def build_kpextractor128_decoupled():
    inp = ll.InputLayer(shape=(None, 1, 128, 128), name='input')
    # alternate pooling and conv layers to minimize parameters
    filter_pad = lambda x, y: (x//2, y//2)
    filter3 = (3, 3)
    same_pad3 = filter_pad(*filter3)
    conv1 = ll.Conv2DLayer(inp, num_filters=16, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv1')
    mp1 = ll.MaxPool2DLayer(conv1, 2, stride=2, name='mp1') # now down to 64 x 64
    bn1 = ll.BatchNormLayer(mp1, name='bn1')
    conv2 = ll.Conv2DLayer(bn1, num_filters=32, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv2')
    mp2 = ll.MaxPool2DLayer(conv2, 2, stride=2, name='mp2') # now down to 32 x 32
    bn2 = ll.BatchNormLayer(mp2, name='bn2')
    conv3 = ll.Conv2DLayer(bn2, num_filters=64, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv3')
    mp3 = ll.MaxPool2DLayer(conv3, 2, stride=2, name='mp3') # now down to 16 x 16
    bn3 = ll.BatchNormLayer(mp3, name='bn3')
    conv4 = ll.Conv2DLayer(bn3, num_filters=128, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv4')
    mp4 = ll.MaxPool2DLayer(conv4, 2, stride=2, name='mp4') # now down to 8 x 8
    bn4 = ll.BatchNormLayer(mp4, name='bn4')
    conv5 = ll.Conv2DLayer(bn4, num_filters=256, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv5')
    mp5 = ll.MaxPool2DLayer(conv5, 2, stride=2, name='mp5') # down to 4 x 4
    bn5 = ll.BatchNormLayer(mp5, name='bn5')

    conv6 = ll.Conv2DLayer(bn5, num_filters=512, filter_size=filter3, pad=same_pad3, W=Orthogonal(), nonlinearity=rectify, name='conv6')
    mp6 = ll.MaxPool2DLayer(conv6, 2, stride=2, name='mp6') # down to 4 x 4
    bn6 = ll.BatchNormLayer(mp6, name='bn6')
    dp0 = ll.DropoutLayer(bn6, p=0.5, name='dp0')

    # now let's bring it down to a FC layer that takes in the 2x2x64 mp4 output
    fc1 = ll.DenseLayer(dp0, num_units=256, nonlinearity=rectify, name='fc1')
    bn1_fc = ll.BatchNormLayer(fc1, name='bn1_fc')
    dp1 = ll.DropoutLayer(bn1_fc, p=0.5, name='dp1')
    # so what we're going to do here instead is break this into three separate layers (each 32 units)
    # then each of these layers goes into a separate out, and out_rs will be a merge and then reshape
    fc2_left = ll.DenseLayer(dp1, num_units=32, nonlinearity=rectify, name='fc2_left')
    fc2_right = ll.DenseLayer(dp1, num_units=32, nonlinearity=rectify, name='fc2_right')
    fc2_notch = ll.DenseLayer(dp1, num_units=32, nonlinearity=rectify, name='fc2_notch')

    out_left = ll.DenseLayer(fc2_left, num_units=2, nonlinearity=linear, name='out_left')
    out_right = ll.DenseLayer(fc2_right, num_units=2, nonlinearity=linear, name='out_right')
    out_notch = ll.DenseLayer(fc2_notch, num_units=2, nonlinearity=linear, name='out_notch')

    out = ll.ConcatLayer([out_left, out_right, out_notch], axis=1, name='out')
    out_rs = ll.ReshapeLayer(out, ([0], 3, 2), name='out_rs')

    return out_rs

#----------- TRAILING EDGE SCORER

class Softmax4D(ll.Layer):
    def get_output_for(self, input, **kwargs):
        si = input.reshape((input.shape[0], input.shape[1], -1))
        shp = (si.shape[0], 1, si.shape[2])
        exp = T.exp(si - si.max(axis=1).reshape(shp))
        softmax_expression = (exp / (exp.sum(axis=1).reshape(shp) + 1e-7) ).reshape(input.shape)
        return softmax_expression

def crossentropy_flat(pred, true):
    # basically we have a distribution output that's in the shape batch, prob, h, w
    # it doesn't look like we can apply the nnet categorical cross entropy easily on a tensor4
    # so we'll have to flatten it out to a tensor2, which is a pain in the ass but easily done

    pred2 = pred.dimshuffle(1,0,2,3).flatten(ndim=2).dimshuffle(1,0)
    true2 = true.dimshuffle(1,0,2,3).flatten(ndim=2).dimshuffle(1,0)

    return T.nnet.categorical_crossentropy(pred2, true2)


def build_segmenter_simple():
    inp = ll.InputLayer(shape=(None, 1, None, None), name='input')
    conv1 = ll.Conv2DLayer(inp, num_filters=4, filter_size=(7,7), pad='same', W=Orthogonal(), nonlinearity=rectify, name='conv1')
    conv2 = ll.Conv2DLayer(conv1, num_filters=8, filter_size=(5,5), pad='same', W=Orthogonal(), nonlinearity=rectify, name='conv2')
    conv3 = ll.Conv2DLayer(conv2, num_filters=16, filter_size=(5,5), pad='same', W=Orthogonal(), nonlinearity=rectify, name='conv3')
    conv4 = ll.Conv2DLayer(conv3, num_filters=8, filter_size=(5,5), pad='same', W=Orthogonal(), nonlinearity=rectify, name='conv4')
    conv5 = ll.Conv2DLayer(conv4, num_filters=8, filter_size=(3,3), pad='same', W=Orthogonal(), nonlinearity=rectify, name='conv5')
    conv6 = ll.Conv2DLayer(conv5, num_filters=4, filter_size=(3,3), pad='same', W=Orthogonal(), nonlinearity=rectify, name='conv6')

    # our output layer is also convolutional, remember that our Y is going to be the same exact size as the
    conv_final = ll.Conv2DLayer(conv6, num_filters=2, filter_size=(3,3), pad='same', W=Orthogonal(), name='conv_final', nonlinearity=linear)
    # we need to reshape it to be a (batch*n*m x 3), i.e. unroll s.t. the feature dimension is preserved
    softmax = Softmax4D(conv_final, name='4dsoftmax')

    return softmax


