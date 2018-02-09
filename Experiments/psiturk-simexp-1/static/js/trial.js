/*

Includes code that runs

*/

var DEFAULT_TRIAL_INFO = {
    score_initialization: 100, // The initial score for each trial
    score_dec_per_s: 10,       // The score decrement per second of waiting
    score_dec_per_exp: 10,     // The score decrement for each experiment run
    score_loss_for_miss: -10,  // The score loss if the shot is missed
    time_until_shot: 3,        // The amount of time allowed between pressing the button and taking a shot
    physics_travel_time: 5,    // The time to run physics during experiments or shots
    physics_px_per_s: 600,     // Velocity of the ball during experiments or shots
    simulation_hz: 40,         // The hertz to run the physics simulation at
    countdown_hz: 10,          // THe hertz to do the score countdown
    arrow_length: 30,          // Length of the arrow drawn to show direction the ball will go
    shot_radius: 200           // The distance between the mouse and ball to take a shot (in px)
}

WAIT_AFTER_PHYSICS_END = 200 // ms to wait before resetting after physics ends

/**
 * segment_angle - Returns the angle based on a vector defined by two points
 *
 * @param  {[x,y]} p1 Originating point
 * @param  {[x,y]} p2 End point
 * @return {float}    Angle in radians of the segment
 */
function segment_angle(p1, p2) {
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return Math.atan2(dy, dx)
}

function dummy_function(event) {
    return
}

function get_time() {
    var d = new Date()
    return d.getTime()
}

/**
 * Trial - Wrapper class for running logic for individual trials
 *
 * @param  {html element} table_object       Element representing the table canvas
 * @param  {html element} table_surround_object  Element for the div surrounding the table
 * @param  {html element} score_object       Element box for displaying the score
 * @param  {html element} shot_button_object Element for button that is clicked to start the shot
 * @param  {html element} text_field         Element for displaying text behind
 * @param  {html element} bottom_elements    Element for storing the score & shot button
 * @param  {object} trial_info               Dictionary with elements for score_initialization, score_dec_per_s, score_dec_per_exp, score_loss_for_miss, time_until_shot, physics_travel_time
 */
Trial = function(table_object, table_surround_object, score_object, shot_button_object, text_field, bottom_elements, trial_info) {
    if (typeof(trial_info)==="undefined") trial_info = DEFAULT_TRIAL_INFO

    // Initialize variables
    this.table_ele = table_object
    this.surround_ele = table_surround_object
    this.score_disp = score_object
    this.shot_but = shot_button_object
    this.score = trial_info.score_initialization
    this.text_field = text_field
    this.bottom = bottom_elements
    this.trial_info = trial_info

    // Status codes:
    //  0: Initializing -- nothing happening
    //  1: Play phase -- waiting
    //  2: Play phase -- simulating
    //  3: Shot phase -- waiting
    //  4: Shot phase -- simulating
    //  5: End
    //  101: Intro: just display
    //  102: Intro: take one shot
    //  103: Intro: have taken a shot
    this.status = 0

    this.failure_timeout = null // Placeholder for shot failure timeout
    this.decrement_interval = null // Placeholder for score decrement interval

    this.return_data = {
        experiments: [],
        shot_time: 0,
        num_experiments: 0,
        points_left: 0,
        score: 0,
        accurate: false,
        shot_angle: 0,
        time_up: false,
        shot_timeout: false
    }

    this.stored_table = null

    this.start_time = 0
    this.end_time = 0
    this.run_callback = dummy_function

    this._write_score()

    var that = this
    // Make the table Object
    this.table = new Table('tmp', that.table_ele.width, that.table_ele.height, that.table_ele[0])

    // Set up the mouse events
    this.table_ele.mousemove(function(event){
        that._mouse_move(that, event)}
    )
    this.table_ele.mouseout(function(event){that._mouse_exit(that, event)})
    this.table_ele.click(function(event){that._mouse_click(that, event)})

    // Set up the button events
    this.shot_but.click(function(event){that._start_shot(that, event)})
}

 /**
  * Trial.prototype.loadTrial - Load a specific trial into this Trial object
  *
  * @param  {string} trial_name       Name of the trial to load
  * @param  {TrialCollection} trial_collection The collection to load from
  * @param  {type} callback         Function that gets called when the trial finishes running
  */

Trial.prototype.loadTrial = function(trial_name, trial_list, callback) {
    // Load in the trial from the TrialList
    this.table = trial_list.loadTrial(trial_name, this.table_ele[0])
    this.stored_table = this.table.clone()
    this.reset()
    this.run(callback)
}


/**
 * Trial.prototype.reset - resets the trial back to the initial condition
 *
 */
Trial.prototype.reset = function() {
    clearInterval(this.decrement_interval)
    clearTimeout(this.failure_timeout)
    this.score = this.trial_info.score_initialization
    this.status = 0
    this.start_time = 0
    this.end_time = 0
    this.run_callback = dummy_function
    this._set_highlight(false)
    this.return_data = {
        experiments: [],
        shot_time: 0,
        num_experiments: 0,
        points_left: 0,
        score: 0,
        accurate: false,
        shot_angle: 0,
        time_up: false,
        shot_timeout: false
    }
    this.draw()
}


Trial.prototype.draw = function() {
    this.table.draw()
}

Trial.prototype.simulate = function(that, callback) {
    // Break simulation if status changes
    if (that.status === 2 | that.status === 4 | that.status === 103) {
        var hz = that.trial_info.simulation_hz
        var ms_next = 1./hz
        // Step forwards
        var r = that.table.step(ms_next, that.trial_info.physics_travel_time)
        that.draw()
        if (r === GREENGOAL) {
            setTimeout(function(){callback(true)}, WAIT_AFTER_PHYSICS_END)
        } else if (r === REDGOAL | r === TIMEUP) {
            setTimeout(function(){callback(false)}, WAIT_AFTER_PHYSICS_END)
        } else {
            setTimeout(function(){that.simulate(that, callback)}, ms_next)
        }
    }
}

Trial.prototype.run = function(callback) {
    this.status = 1
    this.start_time = get_time()
    this.start_score_countdown()
    var that = this
    this.run_callback = callback
}

Trial.prototype.start_score_countdown = function() {
    var timeout = 1000 * (1/this.trial_info.countdown_hz)
    var score_per_tick = this.trial_info.score_dec_per_s / this.trial_info.countdown_hz
    var that = this
    var dec_func = function() {
        that.score -= score_per_tick
        that._write_score()
        if (that.score <= 0) {
            that.time_out()
        }
    }
    that.decrement_interval = setInterval(dec_func, timeout)
}

Trial.prototype.time_out = function() {
    // Leave the experiment with a time_up flag
    this.score = 0
    this.return_data.time_up = true
    this._write_score()
    //this.return_data.points_left = this.score
    //this.return_data.score = this.trial_info.score_loss_for_miss
    clearInterval(this.decrement_interval)
    //this.status = 5
    var that = this
    /*
    that.showinstruct(
        "You let your points run out and have lost " + (-that.trial_info.score_loss_for_miss) + " points<br><br>Click to continue",
        (0,0,0),(255,255,255),
        function() {that.run_callback(that.return_data)}
    )
    */
   that._start_shot(that)
}


/**
 * Trial.prototype.get_ball_pos - Function for quickly getting the position of the ball
 *
 * @return {[x,y]}  The position of the ball on the table
 */
Trial.prototype.get_ball_pos = function() {
    var pos = this.table.ball.getpos()
    return [pos.x, pos.y]
}

// Private method for getting the mouse position relative to the table element
Trial.prototype._get_mouse_relative_to_table = function(mpos) {
    var offset = this.table_ele.offset()
    return [mpos[0]-offset.left, mpos[1]-offset.top]
}

// Private method for checking if mouse is within acceptable distance of ball
Trial.prototype._is_mouse_close = function(mpos, bpos) {
    var req_dist = this.trial_info.shot_radius
    var dx = mpos[0] - bpos[0], dy = mpos[1] - bpos[1]
    var dist_sq = dx*dx + dy*dy
    return (dist_sq <= req_dist*req_dist)
}

// Draws an arrow from the ball in the direction of the mouse
Trial.prototype._mouse_move = function(that, event) {
    // Only works when not simulating
    if (that.status === 1 | that.status === 3 | that.status === 102) {
        var mpos = that._get_mouse_relative_to_table([event.clientX, event.clientY])
        var bpos = that.get_ball_pos()
        that.draw()
        // Only show the line if close enough
        if (that._is_mouse_close(mpos, bpos)) {
            var ang = segment_angle(bpos, mpos)
            // Calculate the line segment to draw
            var lx = that.trial_info.arrow_length * Math.cos(ang)
            var ly = that.trial_info.arrow_length * Math.sin(ang)
            endpt = [bpos[0] + lx, bpos[1] + ly]
            // Do the drawing
            var ctx = that.table_ele[0].getContext('2d')
            var lastStyle = ctx.strokeStyle
            ctx.strokeStyle = "blue"
            var lastWid = ctx.lineWidth
            ctx.lineWidth = 5
            ctx.beginPath()
            ctx.moveTo(bpos[0],bpos[1])
            ctx.lineTo(endpt[0], endpt[1])
            ctx.stroke()
            ctx.strokeStyle = lastStyle
            ctx.lineWidth = lastWid
        }

    }
}

Trial.prototype._mouse_exit = function(that, event) {
    // Redraw so old arrows aren't around
    that.draw()
}

Trial.prototype._mouse_click = function(that, event) {
    // Only works when not simulating
    if (that.status === 1 | that.status === 3 | that.status === 102) {

        var mpos = that._get_mouse_relative_to_table([event.clientX, event.clientY])
        var bpos = that.get_ball_pos()
        if (that._is_mouse_close(mpos, bpos)) {
            // Stop score countdown
            clearInterval(that.decrement_interval)
            var ang = segment_angle(bpos, mpos)

            // Calculate the velocity of the ball
            var vx = that.trial_info.physics_px_per_s * Math.cos(ang)
            var vy = that.trial_info.physics_px_per_s * Math.sin(ang)
            that.table.ball.setvel(vx, vy)
            var cur_time = get_time()
            var this_time = cur_time - that.start_time

            var after_run

            if (that.status === 1) {
                // Take off points
                that.score -= that.trial_info.score_dec_per_exp
                if (that.score <= 0) {
                    that.time_out()
                    //that.score = 0
                    //that._write_score()
                    //that._start_shot(that)
                    return
                }
                that._write_score()
                // Go back to the playground
                after_run = function(outcome) {
                    // Record the data
                    that.return_data.experiments.push({
                        Angle: ang,
                        ExpTime: this_time,
                        Outcome: outcome
                    })
                    that.return_data.num_experiments += 1
                    that.status = 1
                    that.table = that.stored_table.clone()
                    that.draw()
                    that.start_score_countdown()
                }
            }
            if (that.status === 3) {
                // Clear the failure timeout
                clearTimeout(that.failure_timeout)
                that.return_data.shot_time = cur_time - that.end_time
                // Finish off
                after_run = function(outcome) {
                    var finish_text
                    that.score = Math.ceil(that.score) // To avoid fractions
                    if (outcome) {
                        finish_text = "You made the shot and earned " + that.score + " points!<br><br>Click to continue"
                    } else {
                        finish_text = "You missed the shot and lost " + (-that.trial_info.score_loss_for_miss) + " points<br><br>Click to continue"
                    }

                    that.showinstruct(
                        finish_text,(0,0,0),(255,255,255),function() {
                            that.return_data.shot_angle = ang
                            that.return_data.accurate = outcome
                            that.return_data.points_left = Math.ceil(that.score)
                            if (outcome) {
                                that.return_data.score = Math.ceil(that.score)
                            } else {
                                that.return_data.score = that.trial_info.score_loss_for_miss
                            }
                            that.status = 5
                            that.run_callback(that.return_data)
                        })
                  }
            }
            if (that.status === 102) {
              after_run = function(outcome) {
                that.return_data.accurate = outcome
                that.run_callback(that.return_data)
              }
            }
            that.status += 1
            that.simulate(that, after_run)
        }
    } else if (that.status === 101) {
      that.run_callback(that.return_data)
    }
}

Trial.prototype._set_highlight = function(is_on) {
    if (typeof(is_on) === "undefined") is_on = true
    if (is_on) {
        this.surround_ele.css('background-color', 'gold')
    } else {
        this.surround_ele.css('background-color', 'white')
    }
}

Trial.prototype._start_shot = function(that, event) {
    // Only works if in the play period
    if (that.status === 1 | that.status === 2) {
        clearInterval(that.decrement_interval)
        if (that.status === 2) that._end_simulation(that)
        that.status = 3
        that._set_highlight(true)
        that.failure_timeout = window.setTimeout(function(){that._shot_timeout(that)}, that.trial_info.time_until_shot*1000)
    }
    that.end_time = get_time()
    that.return_data.play_time = that.end_time - that.start_time
}

Trial.prototype._shot_timeout = function(that) {
    // Leave the experiment with a shot_timeout flag
    this.return_data.shot_timeout = true
    this.return_data.points_left = this.score
    this.return_data.score = this.trial_info.score_loss_for_miss
    this.status = 5
    var that = this
    this.showinstruct(
        "You need to take your shot faster after it is available!<br><br>You lost " + (-this.trial_info.score_loss_for_miss) + " points<br><br>Click to continue",
        (0,0,0), (255,255,255), function() {that.run_callback(that.return_data)}
    )
}

Trial.prototype._write_score = function() {
    this.score_disp[0].innerHTML = "Score: " + Math.ceil(this.score)
}

/*

Functions for handling text & instructions

*/

Trial.prototype.displaytext = function(text, textcol, bkcol,hideall) {
    if (typeof(bkcol)==='undefined') bkcol = "white"
    if (typeof(textcol)==='undefined') textcol = "black"
    if (text.substring(0,6) === "<span>") htmtext = text
    else htmtext = "<span>"+text+"</span>"
    var wid = this.table_ele.width
    var hgt = this.table_ele.height
    this.surround_ele.hide(0)
    if (typeof(hideall)!== "undefined" & hideall) {
        this.bottom.hide(0)
    }


    tf = this.text_field
    tf.html(htmtext)
    tf.css({'background-color':bkcol,'color':textcol})
    tf.show(0)

}
Trial.prototype.hidetext = function() {
    this.surround_ele.show(0)
    this.table_ele.show(0)
    this.bottom.show(0)
    this.text_field.hide(0)
}
Trial.prototype.showinstruct = function(text,textcol,bkcol, callback, hideall) {
    this.displaytext(text,textcol,bkcol,hideall)
    // Wait until a click
    var that = this

    that.text_field.unbind('click')
    that.text_field.click(function(event) {
        that.hidetext()
        that.text_field.click(dummy_function)
        callback()
    })
}
Trial.prototype.replaceText = function(newtext,textcol,bkcol) {
    this.oldtext = this.text_field.html()
    this.displaytext(newtext,textcol,bkcol)
}
Trial.prototype.restoreText = function(textcol,bkcol) {
    this.displaytext(this.oldtext,textcol,bkcol)
    this.oldtext = ''
}
