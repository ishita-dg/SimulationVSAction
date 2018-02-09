/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */



/**
 * Function to check the window size, and determine whether it is
 * large enough to fit the given experiment. If the window size is not
 * large enough, it hides the experiment display and instead displays
 * the error in the #window-error DOM element. If the window size is
 * large enough, then this centers the experiment horizontally and
 * vertically.
 *
 * From Jessica Hamrick - thanks Jess!
 *
 * @param {Experiment} exp - The experiment object
 */

windowsizer = function(minx, miny,exp) {
    this.x = minx
    this.y = miny
    this.tbshown = false
    this.replaced = false
    this.exp = exp

    console.log($(window).width())
    console.log($(window).height())

    this.checkSize = function(wsme) {
        var maxWidth = $(window).width(),
            maxHeight = $(window).height()

        $("#textfield").width(Math.min(1000,maxWidth))

        if ((minx > maxWidth) || (miny > maxHeight)) {
            wsme.exp.badtrial = true
            if ($("#table").is(":visible")) {
                $("#table").hide(0)
                wsme.tbshown = true
            }

            if (!wsme.replaced) {
                wsme.exp.trial.replaceText('Your window is too small for this experiment. Please make it larger or zoom out from the "View" menu.')
                wsme.replaced = true
            }

            $("#textfield").show(0)
            return
        }

        if (wsme.replaced) {
            wsme.exp.trial.restoreText()
            wsme.replaced = false
        }
        if (wsme.tbshown) {
            $("#canvas_surround").show(0)
            $("#table").show(0)
            $("#textfield").hide(0)
        }

        wsme.tbshown = false


    }
}

// From http://stackoverflow.com/questions/2450954/how-to-randomize-shuffle-a-javascript-array
function shuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex

  // While there remain elements to shuffle...
  while (0 !== currentIndex) {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex)
    currentIndex -= 1

    // And swap it with the current element.
    temporaryValue = array[currentIndex]
    array[currentIndex] = array[randomIndex]
    array[randomIndex] = temporaryValue
  }

  return array
}

Experiment = function(triallist, config, table, table_surround, score_counter, shot_button,
        total_counter, progress_counter, bottom_div, text_field, ptobj) {

    this.pt = ptobj
    this.sc_ele = $("#"+score_counter)
    this.sb_ele = $("#"+shot_button)
    this.tc_ele = $("#"+total_counter)
    this.pc_ele = $("#"+progress_counter)
    this.tb_ele = $("#"+table)
    this.sur_ele = $("#"+table_surround)
    this.bd_ele = $("#"+bottom_div)
    this.text_ele = $("#"+text_field)
    var that = this


    this.config = config
    this.trlist = ajaxJson(triallist)

    this.trlist = shuffle(this.trlist)
    this.tridx = 0
    this.score = 0
    this.num_trials = this.trlist.length
    this.blank_counters()

    load_list = this.trlist.slice()
    load_list.push('intro_1', 'intro_2', 'intro_3', 'intro_4', 'intro_5', 'intro_6', 'intro_7')

    this.loaded_trials = new TrialList(load_list, 'static/trials')

    this.badtrial = false // Holder for if window is too small or minimzied

    // Load in the trial object
    this.trial = new Trial(this.tb_ele,this.sur_ele,this.sc_ele,this.sb_ele,this.text_ele,this.bd_ele,this.config)

}

Experiment.prototype.start_trials = function() {
    //this.trial.loadTrial('trials/'+this.trlist[0]+'.json')
    var that = this
    this.update_progress()
    this.update_total_score()
    this.badtrial = false
    var fn = function(record) {
        // From start_trials
        that.record_trial(that, record)
    }
    that.trial.loadTrial(that.trlist[0],that.loaded_trials,fn)
}

Experiment.prototype.trial_run = function(that) {
    that.badtrial = false
    var fn = function(record) {
        // From trial_run
        that.record_trial(that, record)
    }
    that.trial.run(fn)
}

Experiment.prototype.next_trial = function(that) {
    that.badtrial = false // Reset badness
    that.tridx++
    if (that.tridx >= that.trlist.length) {
        that.end_exp()
        return
    }

    //me.trial.loadTrial('trials/'+me.trlist[me.tridx]+'.json')
    that.update_progress()
    var fn = function(record) {
        // From next_trial
        that.record_trial(that, record)
    }
    that.trial.loadTrial(that.trlist[that.tridx],that.loaded_trials,fn)
}

Experiment.prototype.record_trial = function(that, record) {
    var trname = that.trial.table.name

    assert(that.trial.status === 5, 'Cannot record trial that is not finished')

    var sc = record.score
    record.trial_order = that.tridx
    record.isintro = false
    record.badtrial = that.badtrial
    record.trial_name = trname
    that.score += sc
    that.update_total_score()

    // Insert psiturk recording code here
    //console.log(resps)
    //console.log(realgoal)
    that.pt.recordTrialData(record)

    var bi

    if (that.badtrial) {
        bi = 'Please keep the window open, on top of the screen, and large enough to see everything'
        that.trial.showinstruct(bi,'black','white',function() {that.next_trial(that)})
        return
    }

    that.pt.saveData({
        error: function() {console.log('Error recording data')}
    })
    that.next_trial(that)
}

Experiment.prototype.end_exp = function() {
    var that = this
    this.trial.showinstruct('Congrats! You are now done!<br><br>Click the screen to return to Mechanical Turk','black','white',
        that.pt.completeHIT)
}

Experiment.prototype.instructions = function() {
    var that = this
    //that.start_trials(that)
    that.run_intro(that, 1)
}

Experiment.prototype.update_total_score = function() {
    this.tc_ele[0].innerHTML = "Total Score:<br>" + this.score
}

Experiment.prototype.update_progress = function() {
    this.pc_ele[0].innerHTML = "Progress<br>" + (this.tridx+1) + " of " + this.num_trials
}

Experiment.prototype.blank_counters = function() {
    this.tc_ele[0].innerHTML = ""
    this.pc_ele[0].innerHTML = ""
}

/*

Instructions:

Setup: hide score, take shot, progress, total_score

 1) Welcome, simple intro of trying to shoot a ball into the green goal
 2) Show a really simple trial: mostly green with a splash of red (Intro1)
 3) Shoot by clicking near the ball -- will see directional arrow if close enough
 4) Intro1: Try a shot
 5) Describe full exp: in the end, you only get one shot to make it in green, and lose points if you hit red.
 6) But you can play around first and think about your shot or try certain shots out. Only have limited time, and points count down, plus costs X points when you try out a shot
 7) Once you think you know what you're doing, click take a shot -- you then have 3 seconds to do that before you lose. The shot being real is signified by a yellow outline around the field. If your points get to 0, it automatically becomes yellow and you must immediately take the shot to possibly lose no points
 8) Try Intro1 for real
 9) Four more sample trials upcoming
 10-13) Do those trials
 14) Get started!

 */

Experiment.prototype.run_intro = function(that, counter) {
  var cb = function(i) {
    that.run_intro(that, counter + 1)
  }
  if (counter === 1) {
    // Hide the bottom elements
    that.sc_ele.hide(0)
    that.sb_ele.hide(0)
    that.tc_ele.hide(0)
    that.pc_ele.hide(0)
    // Display instructions
    var itxt = "Welcome! In this experiment, you will play a game where you will launch a blue ball so that it lands in a green goal. There will also be red goals that you must avoid, and black obstacles and outside walls that the ball will bounce off of.<br><br>Click the mouse to see an example level, then click the mouse while it is inside of the level to continue."
    that.trial.showinstruct(itxt, 'black', 'white', cb)
  } else if (counter === 2) {
    // Load in intro_1
    that.trial.loadTrial('intro_1', that.loaded_trials, cb)
    that.trial.status = 101 // Pass through
  } else if (counter === 3) {
    var itxt = "You can aim your shot with your mouse by bringing your cursor close to the ball and clicking to shoot the ball in the direction of the cursor.<br><br>If your mouse is close enough, a line will come out from the ball in the direction it will be shot. If you don't see that aiming line, you cannot shoot the ball.<br><br>Click the mouse to continue, then try taking a shot."
    that.trial.showinstruct(itxt, 'black', 'white', cb)
  } else if (counter === 4) {
    that.trial.loadTrial('intro_1', that.loaded_trials, cb)
    that.trial.status = 102 // Single shot
  } else if (counter === 5) {
    var itxt = "In the real task, you will build up to taking a single shot for each level where you will gain points if you make it into the green goal, and lose points if the ball hits the red goal (or takes too long to reach either goal).<br><br>Click the mouse to continue."
    that.trial.showinstruct(itxt, 'black', 'white', cb)
  } else if (counter === 6) {
    var itxt = "Before you take your final shot, you can play around in the level. You can spend time thinking about the shot you want to make, or even try taking practice shots.<br><br>But be careful not to do too much thinking or practicing: you will start with 100 points and will lose points over time. Also, each time you take a practice shot you will lose " + that.config.score_dec_per_exp + " points.<br><br>Click the mouse to continue."
    that.trial.showinstruct(itxt, 'black', 'white', cb)
  } else if (counter === 7) {
    // Show the score element & shot button
    that.trial.score = 0
    that.trial._write_score()
    that.sb_ele.show(0)
    that.sc_ele.show(0)
    var itxt = "When you are ready to take your final shot, you can click on the button that says \"Take a shot\" below the level screen. Once you click this button, the outside of the level will turn yellow and you will have three seconds to act.<br><br>If you make that shot in the green goal, you get however many points are remaining on the counter on the bottom left of the screen. If you miss the shot (or wait too long to take it), you will lose 10 points.<br><br>Click the mouse to try this out -- and be sure to take at least one practice shot and get the ball into the green goal!"
    that.trial.showinstruct(itxt, 'black', 'white', cb)
  } else if (counter === 8) {
    that.badtrial = false
    // Callback checks on what participant does
    cb = function(rdat) {
      if (rdat.shot_timeout) {
        that.trial.showinstruct("You must make your final shot!<br><br>Click to try again.", 'black', 'white', function(i){that.run_intro(that, counter)})
      } else if (!rdat.accurate) {
        that.trial.showinstruct("You must make your final shot into the green goal!<br><br>Click to try again.", 'black', 'white', function(i){that.run_intro(that, counter)})
      } else if (rdat.num_experiments === 0) {
          that.trial.showinstruct("You must take at least one practice shot!<br><br>Click to try again.", 'black', 'white', function(i){that.run_intro(that, counter)})
      } else {
        that.record_intro(that, rdat, counter + 1)
      }
    }
    that.trial.loadTrial('intro_1', that.loaded_trials, cb)
  } else if (counter === 9) {
    var itxt = "Just a warning: if your points run down to zero, the outline will turn yellow and you will be forced to make your final shot. If you make this, nothing happens to your score, but if you miss it, you lose 10 points.<br><br>Now click the mouse to begin four more practice trials."
    that.trial.showinstruct(itxt, 'black', 'white', cb)
  } else if (counter <= 15) {
    that.badtrial = false
    var trname = 'intro_' + (counter - 8)
    cb = function(rdat) {
      that.record_intro(that, rdat, counter + 1)
    }
    that.trial.loadTrial(trname, that.loaded_trials, cb)
  } else if (counter === 16) {
    that.tc_ele.show(0)
    that.pc_ele.show(0)
    that.score = 0
    var itxt = "Now you are about ready to start the real trials. You will have " + that.num_trials + " levels to go through, and can see your total score and progress in the lower right.<br><br>Click the mouse to begin!"
    that.trial.showinstruct(itxt, 'black', 'white', function() {that.start_trials(that)})
  }
}

Experiment.prototype.record_intro = function(that, record, icounter) {
    var trname = that.trial.table.name

    assert(that.trial.status === 5, 'Cannot record trial that is not finished')

    var sc = record.score
    record.trial_order = that.tridx
    record.isintro = true
    record.badtrial = that.badtrial
    record.trial_name = trname
    that.score += sc
    that.update_total_score()

    that.pt.recordTrialData(record)

    var bi

    if (that.badtrial) {
        bi = 'Please keep the window open, on top of the screen, and large enough to see everything'
        that.trial.showinstruct(bi,'black','white',function() {that.run_intro(that, icounter)})
        return
    }

    that.pt.saveData({
        error: function() {console.log('Error recording data')}
    })
    that.run_intro(that, icounter)
}
