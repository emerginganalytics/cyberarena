let canvas = document.getElementById('game');
let context = canvas.getContext('2d');

let grid = 16;
let count = 0;
let score=0;
let max=0;

let snake = {
  x: 160,
  y: 160,

  // snake velocity. moves one grid length every frame in either the x or y direction
  dx: grid,
  dy: 0,

  // keep track of all grids the snake body occupies
  cells: [],

  // length of the snake. grows when eating an apple
  maxCells: 4
};
let apple = {
  x: 320,
  y: 320
};
// random int
function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min)) + min;
}
// game loop
function loop() {
  requestAnimationFrame(loop);
  // slow game loop to 15 fps instead of 60 (60/15 = 4)
  if (++count < 4) {
    return;
  }
  count = 0;
  context.clearRect(0,0,canvas.width,canvas.height);
  // move snake by it's velocity
  snake.x += snake.dx;
  snake.y += snake.dy;
  // wrap snake position horizontally on edge of screen
  if (snake.x < 0) {
    snake.x = canvas.width - grid;
  }
  else if (snake.x >= canvas.width) {
    snake.x = 0;
  }

  // wrap snake position vertically on edge of screen
  if (snake.y < 0) {
    snake.y = canvas.height - grid;
  }
  else if (snake.y >= canvas.height) {
    snake.y = 0;
  }
  // keep track of where snake has been. front of the array is always the head
  snake.cells.unshift({x: snake.x, y: snake.y});
  // remove cells as we move away from them
  if (snake.cells.length > snake.maxCells) {
    snake.cells.pop();
  }
  // draw apple
  context.fillStyle = 'red';
  context.fillRect(apple.x, apple.y, grid-1, grid-1);
  // draw snake one cell at a time
  context.fillStyle = 'green';
  snake.cells.forEach(function(cell, index) {

    context.fillRect(cell.x, cell.y, grid-1, grid-1);
    // snake ate apple
    if (cell.x === apple.x && cell.y === apple.y) {
      snake.maxCells++;
	  score+=10;
	  if (score >= 100000) {
	      flag(score);
      }
	  //max=score;
	  document.getElementById('score').innerHTML=score;

      // canvas is 400x400 which is 25x25 grids
      apple.x = getRandomInt(0, 25) * grid;
      apple.y = getRandomInt(0, 25) * grid;
    }
    // check collision with all cells after this one
    for (let i = index + 1; i < snake.cells.length; i++)
	{

      // reset game on body collision
      if (cell.x === snake.cells[i].x && cell.y === snake.cells[i].y)
	 {

	    if(score>max)
	    {
	     max=score;
	    }
    	snake.x = 160;
        snake.y = 160;
        snake.cells = [];
        snake.maxCells = 4;
        snake.dx = grid;
        snake.dy = 0;
		score=0;
        apple.x = getRandomInt(0, 25) * grid;
        apple.y = getRandomInt(0, 25) * grid;
	    document.getElementById('high').innerHTML=max;
      }
    }
  }
  );
}
// listen to keyboard events to move the snake
document.addEventListener('keydown', function(e) {
  // keys for movement & disable backtracking

  // left arrow key
  if (e.keyCode === 37 && snake.dx === 0) {
    snake.dx = -grid;
    snake.dy = 0;
  }
  // up arrow key
  else if (e.keyCode === 38 && snake.dy === 0) {
    snake.dy = -grid;
    snake.dx = 0;
  }
  // right arrow key
  else if (e.keyCode === 39 && snake.dx === 0) {
    snake.dx = grid;
    snake.dy = 0;
  }
  // down arrow key
  else if (e.keyCode === 40 && snake.dy === 0) {
    snake.dy = grid;
    snake.dx = 0;
  }
});
// function to check score for flag
function flag(score) {
    let score_data = {'score':score};
    $.ajax('/snake_flag',{
        method: 'POST',
        data: JSON.stringify(score_data),
        dataType: "json",
        contentType: "application/json",
    }).done(function(flag_data){
        $("#flag").html(flag_data.flag);
      })
}
// game start
requestAnimationFrame(loop);