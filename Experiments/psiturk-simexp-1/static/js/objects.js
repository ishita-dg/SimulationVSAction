/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */


/*global check, _, $, cp*/

// Color constants
var BLUE = 'rgb(0,0,255)';
var BLACK = 'rgb(0,0,0)';
var GREEN = 'rgb(0,255,0)';
var RED = 'rgb(255,0,0)';

//  Return constants
var TIMEUP = 101;
var SUCCESS = 102;
var FAILURE = 103;
var OUTOFBOUNDS = 104;
var UNCERTAIN = 105;
var REDGOAL = 201;
var GREENGOAL = 202;
var BLUEGOAL = 203;
var YELLOWGOAL = 204;

// For request animation frame code
var raf = window.requestAnimationFrame || window.mozRequestAnimationFrame ||
          window.webkitRequestAnimationFrame || window.oRequestAnimationFrame;

/*
 *
 * @param {num} x1: x coordinate of point 1
 * @param {num} y1: y coordinate of point 1
 * @param {num} x2: x coordinate of point 2
 * @param {num} y2: y coordinate of point 2
 * @param {num} r: radius of separation
 * @returns {bool}: true if points 1 and 2 are within r px of each other
 */
edistwithin = function(x1,y1,x2,y2,r) {
    var dx2 = (x1-x2)*(x1-x2);
    var dy2 = (y1-y2)*(y1-y2);
    return dx2 + dy2 < r*r;
};

/**
 *
 * @param {type} px - x position of center of ball
 * @param {type} py - y position of center of ball
 * @param {type} vx - x velocity (px/s)
 * @param {type} vy - y velocity (px/s)
 * @param {type} rad - radius in pixels
 * @param {type} space - cp.Space object to attach to
 * @returns {Ball}
 */
Ball = function(px, py, vx, vy, rad, color, elast, space) {

    if (typeof(color)==='undefined') color = 'rgb(0,0,255)';
    if (typeof(elast)==='undefined') elast = 1.;

    // Record inputs
    var pos = new cp.Vect(px,py);
    var vel = new cp.Vect(vx,vy);
    this.rad = rad;
    this.space = space;
    this.col = color;
    this.elast = elast;

    // Add new body to chipmunk space
    var mom = cp.momentForCircle(1,0,this.rad,cp.vzero);
    this.body = new cp.Body(1.0, mom);
    this.circ = new cp.CircleShape(this.body, rad, cp.vzero);
    this.circ.setElasticity(elast);
    this.body.setPos(pos);
    this.body.setVel(vel);
    this.space.addBody(this.body);
    this.space.addShape(this.circ);

};

Ball.prototype.setpos = function(newx, newy) {
    var newpos = new cp.Vect(newx,newy);
    // TO ADD: Error & boundary checking
    this.body.setPos(newpos);
};
Ball.prototype.getpos = function() {
    return this.body.getPos();
};
Ball.prototype.setvel = function(nvx, nvy) {
    var newvel = new cp.Vect(nvx,nvy);
    this.body.setVel(newvel);
};
Ball.prototype.getvel = function() {
    return this.body.getVel();
};
Ball.prototype.getbounds = function() {
    var ctr = this.getpos();
    return [ctr[0]-this.rad,ctr[0]+this.rad,ctr[1]-this.rad,ctr[1]+this.rad];
};
Ball.prototype.draw = function (ctx) {
    ctx.fillStyle = this.col;
    var pos = this.getpos();
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    ctx.arc(pos.x, pos.y, this.rad, 0, 2*Math.PI,true);
    ctx.fill();
};
Ball.prototype.clone = function(newspace) {
    var pos = this.getpos();
    var vel = this.getvel();
    return new Ball(pos.x,pos.y,vel.x,vel.y,this.rad,this.col,this.elast,newspace);
};

/*
 *
 * @param {type} rect: any type of object that has top, bottom, left, right
 *                     (e.g., walls, occluders, goals)
 * @returns {bool} if there's an intersection
 */
Ball.prototype.intersectRect= function(rect) {
    var pos = this.getpos();
    var r = this.rad;
    var top = pos.y-r;
    var bottom = pos.y+r;
    var right = pos.x+r;
    var left = pos.x-r;

    // Collision between bounding rectangles
    if (!(rect.left > right || rect.right < left ||
            rect.top > bottom || rect.bottom < top)) {

        // Cheap non-distance calcs
        //  1) if a vertical collision and center is in, it's a hit
        if ((bottom > rect.top || top < rect.bottom) &&
                pos.x > rect.left && pos.x < rect.right) {return true;}
        // 2) if a horizontal collision and center is in vert, it's a hit
        if ((right > rect.left || left < rect.right) &&
                pos.y > rect.top && pos.y < rect.bottom) {return true;}

        // Otherwise, check if center is less than r from edge points
        if (edistwithin(pos.x,pos.y,rect.left,rect.top,r)) return true;
        if (edistwithin(pos.x,pos.y,rect.right,rect.top,r)) return true;
        if (edistwithin(pos.x,pos.y,rect.left,rect.bottom,r)) return true;
        if (edistwithin(pos.x,pos.y,rect.right,rect.bottom,r)) return true;

        // Passed all checks
        return false;
    }
    return false;
};

/**
 *
 * @param {int} top
 * @param {int} left
 * @param {int} bottom
 * @param {int} right
 * @param {cp.Space} space: space object to attach wall to
 * @returns {Wall}
 */
Wall = function(left, top, right, bottom,color,elast, space) {
    this.top = top;
    this.left = left;
    this.bottom = bottom;
    this.right = right;
    this.space = space;
    this.col = color;
    this.elast = elast;

    this.bb = new cp.bb(left,top,right,bottom);

    this.shape = this.space.addShape(new cp.BoxShape2(this.space.staticBody, this.bb));
    this.shape.setElasticity(elast);
};

Wall.prototype.draw = function(ctx) {
    var w = this.right - this.left;
    var h = this.bottom - this.top;
    ctx.fillStyle = this.col;
    ctx.fillRect(this.left,this.top,w,h);
};
Wall.prototype.clone = function(newspace) {
    return new Wall(this.left,this.top,this.right,this.bottom,this.col,
        this.elast, newspace);
};

Occluder = function(left,top,right,bottom,color) {
   this.top = top;
   this.left = left;
   this.bottom = bottom;
   this.right = right;
   this.col = color;
};
Occluder.prototype.draw = function(ctx) {
    var w = this.right - this.left;
    var h = this.bottom - this.top;
    ctx.fillStyle = this.col;
    ctx.fillRect(this.left,this.top,w,h);
};
Occluder.prototype.clone = function() {
    return new Occluder(this.left,this.top,this.right,this.bottom,this.col);
};

Goal = function(left,top,right,bottom,color,onreturn) {
    this.top = top;
    this.left = left;
    this.bottom = bottom;
    this.right = right;

    this.onret = onreturn;
    if (typeof(color)==='undefined') color = 'rgba(0,0,0,0)';
    this.color = color;
};
Goal.prototype.draw = function(ctx) {
    w = this.right - this.left;
    h = this.bottom - this.top;
    ctx.fillStyle = this.color;
    ctx.fillRect(this.left,this.top,w,h);
};
Goal.prototype.clone = function() {
    return new Goal(this.left,this.top,this.right,this.bottom,this.color,this.onret);
};

Table = function(name,dimx, dimy, canvas, closedends,backgroundcolor, timeres) {
    // Defaults to closed off
    if (typeof(closedends)==='undefined') closedends = [true,true,true,true];

    if (typeof(timeres)!=='undefined') this.tres = timeres;
    else this.tres = 1/1000.;

    if (typeof(backgroundcolor==='undefined')) this.bkc = 'rgb(255,255,255)';
    else this.bkc = backgroundcolor;

    this.name = name;

    this.dims = new cp.Vect(dimx,dimy);
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');

    this.onstep = function() {};
    this.time = 0.;
    this.clocktime = new Date().getTime();

    this.space = new cp.Space();
    this.ball;
    this.walls = [];
    this.goals = [];
    this.occs = [];
    this.ces = closedends;

    var ce;

    this.ends = [];
    if (closedends[0]) {
        ce = this.space.addShape(new cp.SegmentShape(this.space.staticBody,cp.v(-1,-10),cp.v(dimx+1,-10),10));
        ce.setElasticity(1.);
        this.ends[this.ends.length] = ce;
    }
    if (closedends[1]) {
        ce = this.space.addShape(new cp.SegmentShape(this.space.staticBody,cp.v(dimx+10,-1),cp.v(dimx+10,dimy+10),10));
        ce.setElasticity(1.);
        this.ends[this.ends.length] = ce;
    }
    if (closedends[2]) {
        ce = this.space.addShape(new cp.SegmentShape(this.space.staticBody,cp.v(-1,dimy+10),cp.v(dimx+1,dimy+10),10));
        ce.setElasticity(1.);
        this.ends[this.ends.length] = ce;
    }
    if (closedends[3]) {
        ce = this.space.addShape(new cp.SegmentShape(this.space.staticBody,cp.v(-10,-1),cp.v(-10,dimy+1),10));
        ce.setElasticity(1.);
        this.ends[this.ends.length] = ce;
    }

};

Table.prototype.addball = function(px,py,vx,vy,rad,color,elast) {
    if (typeof(color)==='undefined') color = 'rgb(0,0,255)';
    if (typeof(elast)==='undefined') elast = 1.;
    var b = new Ball(px,py,vx,vy,rad,color,elast,this.space);
    if (typeof(this.ball)!=='undefined') console.log('Overwriting ball');
    this.ball = b;
    return b;
};

Table.prototype.addwall = function(left, top, right, bottom,color,elast) {
    if (typeof(color)==='undefined') color = 'rgb(0,0,0)';
    if (typeof(elast)==='undefined') elast = 1.;
    var w = new Wall(left,top,right,bottom,color,elast,this.space);
    this.walls[this.walls.length] = w;
    return w;
};

Table.prototype.addoccluder = function(left,top,right,bottom,color) {
    if (typeof(color)==='undefined') color = 'grey';
    var o = new Occluder(left,top,right,bottom);
    this.occs[this.occs.length] = o;
    return o;
};

Table.prototype.addgoal = function(left,top,right,bottom,color,onreturn) {
    var g = new Goal(left,top,right,bottom,color,onreturn);
    this.goals[this.goals.length] = g;
    return g;
};

Table.prototype.draw = function() {
    var oldcompop = this.ctx.globalCompositeOperation;
    this.ctx.globalCompositeOperation = 'source-over';

    var w, g, o;

    this.ctx.fillStyle = 'white';
    this.ctx.fillRect(0,0,this.dims.x,this.dims.y);
    if (typeof(this.ball)!=='undefined') this.ball.draw(this.ctx);
    for (var i = 0; i < this.walls.length; i++){
        w = this.walls[i];
        w.draw(this.ctx);
    }
    // Other goals, occluders
    for (var i =0; i < this.goals.length; i++) {
        g = this.goals[i];
        g.draw(this.ctx);
    }

    for (var i = 0; i < this.occs.length; i++) {
        o = this.occs[i];
        o.draw(this.ctx);
    }
    this.ctx.globalCompositeOperation = oldcompop;
};

Table.prototype.checkend = function() {
   var g;
   for (j=0;j<this.goals.length;j++) {
       g = this.goals[j];
       if (this.ball.intersectRect(g)) return g.onret;
   }
   return 0;
};

Table.prototype.step = function(t, maxtime) {
    var nsteps = t / this.tres;
    if (nsteps % 1 !== 0) console.log('Steps not evenly divisible... may be off');
    var e;
    for (i=0; i < nsteps; i++) {
        this.onstep();
        this.space.step(this.tres);
        this.time += this.tres;
        e = this.checkend();
        if (e !== 0) return e;
        if (maxtime && this.time > maxtime) return TIMEUP;
    }
    return e;
};

Table.prototype.clone = function() {
    var newtb = new Table(this.name, this.dims.x, this.dims.y,this.canvas, this.ces, this.bkc,this.tres);
    var newsp = newtb.space;
    newtb.ball = this.ball.clone(newsp);
    var i;
    for (i=0;i<this.walls.length;i++) {
        newtb.walls[i] = this.walls[i].clone(newsp);
    }
    for (i=0;i<this.occs.length;i++) {
        newtb.occs[i] = this.occs[i].clone();
    }
    for (i=0;i<this.goals.length;i++) {
        newtb.goals[i] = this.goals[i].clone();
    }
    return newtb;
};

ajaxStruct = function() {
    this.data; // Holder for ajax data
};

preloadTrial = function(jsonfile) {
    var failure = false;
    var trdat = new ajaxStruct();
    $.ajax({
        dataType: "json",
        url: jsonfile,
        async: false,
        success: function(data) {
            trdat.data = data;
        },
        error: function(req) {
            alert('Error loading JSON file; ' + req.status);
            failure = true;
        }
    });
    return trdat.data;
};

var convert_color_to_rgba = function(color_list) {
    assert(color_list.length >=3, "Must have at least RGB colors");
    var alpha = color_list.length == 4 ? color_list[3] : "255";
    var s = "rgba("+color_list[0]+","+color_list[1]+","+color_list[2]+","+alpha+")";
    return s;
};

TrialList = function(trialnames, trialpath) {
    assert(trialnames instanceof Array, "trialnames must be an array");
    this.tnms = trialnames;
    this.trials = [];

    for (var i = 0; i < this.tnms.length; i++) {
        this.trials[i] = preloadTrial(trialpath + '/' + this.tnms[i] + '.json');
    }
};

TrialList.prototype.loadTrial = function(trialname, canvas) {
    var tdat = this.trials[this.tnms.indexOf(trialname)];
    return this.loadFromData(tdat, canvas);
};

TrialList.prototype.loadFromData = function(d, canvas) {
    var tdims = d.Dims;
    var ces = [false,false,false,false];
    var bkar = d.BKColor;
    var bkc = "rgba("+bkar[0]+","+bkar[1]+","+bkar[2]+","+bkar[3]+")";
    for (i=0;i<d.ClosedEnds.length;i++) {
        ces[d.ClosedEnds[i]-1] = true;
    }
    var tab = new Table(d.Name,tdims[0],tdims[1],canvas,ces,bkc);

    // Add the ball
    var b = d.Ball;
    //var bcol = "rgba("+b[3][0]+","+b[3][1]+","+b[3][2]+","+b[3][3]+")";
    var bcol = convert_color_to_rgba(b[3]);
    tab.addball(b[0][0],b[0][1],b[1][0],b[1][1],b[2],bcol,b[4]);

    var w, wcol, o, ocol, g, gcol;

    // Add walls
    for (i=0;i<d.Walls.length;i++) {
        w = d.Walls[i];
        //wcol = "rgba("+w[2][0]+","+w[2][1]+","+w[2][2]+","+w[2][3]+")";
        wcol = convert_color_to_rgba(w[2]);
        tab.addwall(w[0][0],w[0][1],w[1][0],w[1][1],wcol,w[3]);
    }

    // Add occluders
    for (i=0;i<d.Occluders.length;i++) {
        o = d.Occluders[i];
        //ocol = "rgba("+o[2][0]+","+o[2][1]+","+o[2][2]+","+o[2][3]+")";
        ocol = convert_color_to_rgba(o[0]);
        tab.addoccluder(o[0][0],o[0][1],o[1][0],o[1][1],ocol);
    }

    // Add goals
    for (i=0;i<d.Goals.length;i++) {
        g = d.Goals[i];
        //gcol = "rgba("+g[3][0]+","+g[3][1]+","+g[3][2]+","+g[3][3]+")";
        gcol = convert_color_to_rgba(g[3]);
        tab.addgoal(g[0][0],g[0][1],g[1][0],g[1][1],gcol,g[2]);
    }

    // AbnormWalls and Paddles not implemented (yet)
    if (d.AbnormWalls.length !== 0) alert('AbnormWalls not supported');
    if (d.Paddle) alert('Paddle not supported');

    return tab;
};

loadTrial = function(jsonfile,canvas) {
    var failure = false;
    var trdat = new ajaxStruct();
    $.ajax({
        dataType: "json",
        url: jsonfile,
        async: false,
        success: function(data) {
            trdat.data = data;
        },
        error: function(req) {
            alert('Error loading JSON file; ' + req.status);
            failure = true;
        }
    });
    if (failure) return 0;
    var d = trdat.data;

    // Make a new table
    var tdims = d.Dims;
    var ces = [false,false,false,false];
    var bkar = d.BKColor;
    var bkc = "rgba("+bkar[0]+","+bkar[1]+","+bkar[2]+","+bkar[3]+")";
    for (i=0;i<d.ClosedEnds.length;i++) {
        ces[d.ClosedEnds[i]-1] = true;
    }
    var tab = new Table(d.Name,tdims[0],tdims[1],canvas,ces,bkc);

    // Add the ball
    var b = d.Ball;
    var bcol = "rgba("+b[3][0]+","+b[3][1]+","+b[3][2]+","+b[3][3]+")";
    tab.addball(b[0][0],b[0][1],b[1][0],b[1][1],b[2],bcol,b[4]);

    var w, wcol, o, ocol, g, gcol;

    // Add walls
    for (i=0;i<d.Walls.length;i++) {
        w = d.Walls[i];
        wcol = "rgba("+w[2][0]+","+w[2][1]+","+w[2][2]+","+w[2][3]+")";
        tab.addwall(w[0][0],w[0][1],w[1][0],w[1][1],wcol,w[3]);
    }

    // Add occluders
    for (i=0;i<d.Occluders.length;i++) {
        o = d.Occluders[i];
        ocol = "rgba("+o[2][0]+","+o[2][1]+","+o[2][2]+","+o[2][3]+")";
        tab.addoccluder(o[0][0],o[0][1],o[1][0],o[1][1],ocol);
    }

    // Add goals
    for (i=0;i<d.Goals.length;i++) {
        g = d.Goals[i];
        gcol = "rgba("+g[3][0]+","+g[3][1]+","+g[3][2]+","+g[3][3]+")";
        tab.addgoal(g[0][0],g[0][1],g[1][0],g[1][1],gcol,g[2]);
    }

    // AbnormWalls and Paddles not implemented (yet)
    if (d.AbnormWalls.length !== 0) alert('AbnormWalls not supported');
    if (d.Paddle) alert('Paddle not supported');

    return tab;
};
