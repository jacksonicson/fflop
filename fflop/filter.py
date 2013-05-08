class Status(object):
    def __init__(self):
        self.f_agile = None
        self.f_stable = None
        self.b_bar = None
        self.mw = [10]
        self.x_prev = None
        self.x_bar = None
        
        self.ucl = None
        self.lcl = None
        
        self.forecast = 0
        
    def mean(self):
        s = 0
        for x in self.mw:
            s += x
        return float(s) / float(len(self.mw))

class FlipFlop(object):
    def __init__(self, l=0.1, u=0.9):
        self.l = l
        self.u = u
    
    def continous(self, x, status=None):
        '''
        Implementation of the flip flop filter as described by Minkyong Kim and Brian Noble
        EWMA = Exponential Weighted Moving Average
        buffer = Status information that was returned by the previous call 
        '''
        
        # Initialize status
        if status == None:
            status = Status()
        
        # Update agile and stable EWMA
        status.f_agile = self.continous_single_exponential_smoothed(status.f_agile, x, self.u)
        status.f_stable = self.continous_single_exponential_smoothed(status.f_stable, x, self.l)
        
        # Update estimated population mean \bar{x}
        status.x_bar = self.continous_single_exponential_smoothed(status.x_bar, x, 0.5)
        
        # Calculate \bar{MW}
        mw_average = status.mean()
            
        # Update upper and lower control limits 
        # (constants are given by the paper)
        ucl = status.x_bar + 3 * (mw_average / 1.128)
        lcl = status.x_bar - 3 * (mw_average / 1.128)
        status.ucl = ucl
        status.lcl = lcl
        
        # Run flip-flop logic
        # if status.f_agile >= lcl and status.f_agile <= ucl:
        if status.forecast >= lcl and status.forecast <= ucl:
            forecast = status.forecast
            
            # Update moving range
            if status.x_prev != None:
                delta = abs(x - status.x_prev)
                status.mw.append(delta)
                l = 3
                if len(status.mw) > l:
                    status.mw = status.mw[-l:]
                    
        else:
            if status.f_agile >= lcl and status.f_agile <= ucl:
                forecast = status.f_agile
            else:
                forecast = status.f_stable
        
        # Return status and forecast
        status.x_prev = x
        status.forecast = forecast 
        return forecast, status
    
    
    def continous_single_exponential_smoothed(self, f_t, data_t, alpha):
        # Smoothing equation (1)
        # f_t is the forecasted value for f_{t+1}
        
        if f_t == None: 
            return data_t
        
        f_t = alpha * data_t + (1 - alpha) * f_t
        
        return f_t

def flip_flop(readings):
    ff = FlipFlop()
    status = None
    for x in readings:
        forecast, status = ff.continous(x, status) 
    return forecast


