/*
 * Requires:
 *     psiturk.js
 *     utils.js
 */

// Initalize psiturk object
var psiTurk = new PsiTurk(uniqueId, adServerLoc, mode)


psiTurk.preloadPages(["stage.html"])


// Condition list -- cost per experiment
var cost_per_exp = {
  "0": 10,
  "1": 20
}

/*******************
 * Run Task
 ******************/
$(window).load( function(){
    psiTurk.showPage("stage.html")
    $('.field').hide(0)
    var cfg = ajaxJson('../static/json/basic_config.json')
    var ecost = cost_per_exp[condition]
    psiTurk.recordUnstructuredData('experiment_cost', ecost)
    cfg['score_dec_per_exp'] = ecost
    exp = new Experiment('../static/trials/TrList.json', cfg,
        'table', 'canvas_surround', 'score_counter', 'shot_button',
        'total_score', 'progress', 'bottom_elements', 'textfield', psiTurk)
    ws = new windowsizer(1010,700,exp)
    ws.checkSize(ws)
    $(window).resize(function() {ws.checkSize(ws)})
    $(window).blur(function() {exp.badtrial = true})

    exp.instructions()
})
