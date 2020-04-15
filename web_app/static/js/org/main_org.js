function makeField(pf, uf){
    var tableJs = document.createElement('table');
    tableJs.id = 'table_id1';
    for(i = 0; i < pf.length; i++){
        var trJs = document.createElement('tr');
        for(j = 0; j < pf[0].length; j++){
            var tdJs = document.createElement('td');
            tdJs.innerHTML = pf[i][j];
            if(uf[i][j]==1){ // agentの位置の色を変える
                tdJs.style.backgroundColor = '#ff1493';
            }else if(uf[i][j]==2){ // aiの位置の色を変える
                tdJs.style.backgroundColor = '#00bfff';
            }else if(uf[i][j]==5){ // 自分のパネルの色を変える
                tdJs.style.backgroundColor = '#ffb6C1';
            }else if(uf[i][j]==6){  // 相手のパネルの色を変える
                tdJs.style.backgroundColor = '#add8e6';
            }else{
                tdJs.style.backgroundColor = '#ffffff';
            }
            tdJs.onclick = function(){sendAction(this);}
            trJs.appendChild(tdJs);
        }
        tableJs.appendChild(trJs);
    }

    var bodyJs = document.body;
    bodyJs.appendChild(tableJs);
}

function Mclk(Cell) {
    var rowNum = Cell.parentNode.rowIndex;
    var rowINX = '行位置：'+rowNum;//Cellの親ノード'tr'の行位置
    var cellNum = Cell.cellIndex;
    var cellINX = 'セル位置：'+ cellNum;
    var cellCol = Cell.style.backgroundColor;
    console.log(typeof(rowNum))
    console.log(typeof(cellNum))
    console.log(cellCol)
    if(cellCol=='rgb(255, 255, 255)'){ // 選択したタイルの色が白
        Cell.style.backgroundColor = '#ff0000';
    } else if(cellCol=='#ffffff'){ // 選択したタイルの色が白
        Cell.style.backgroundColor = '#ff0000';
    } else if(!cellCol){ 
        Cell.style.backgroundColor = '#ff0000';
    }else{ // 選択したタイルの色が赤
        Cell.style.backgroundColor = '#ffffff';
    }
    // var cellVal = 'セルの内容：'+Cell.innerHTML;
    //取得した値の書き出し
    res = rowINX + ' ' + cellINX + ' ' + 'セルの色: '+ cellCol;
    document.getElementById('clickKekka').innerHTML = res;
    var action = 'move';
    var domain = 'http://localhost:8002/play/move';
    // postForm([cellNum, rowNum], action, domain)

    //Cell.style.backgroundColor = ''

}

function sendAction(Cell){
    var rowNum = Cell.parentNode.rowIndex; // 行位置
    var cellNum = Cell.cellIndex; // 列位置
    var cellCol = Cell.style.backgroundColor; // セルの背景色
    console.log(rowNum)
    console.log(cellNum)
    console.log(cellCol)

    var action = judgeAction(cellCol);
    console.log(action)
    var domain = 'http://localhost:8002/play/move';
    postForm([cellNum, rowNum], action, domain)

}

function judgeAction(colors){
    var actions='';
    if(colors=='rgb(255, 255, 255)' || colors=='#ffffff'){ // 選択したタイルの色が白
        actions = 'move';
    } else if(colors=='#ff1493'){ // 選択したタイルが自分がいる位置
        actions = 'move';
    } else if(colors=='#00bfff'){ // 選択したタイルが相手エージェントのいる位置
        actions = 'remove';
    } else if(colors=='#add8e6'){ // 選択したタイルが相手エージェントのタイル
        actions = 'remove';
    } else if(colors=='#ffb6C1'){ // 選択したタイルが自分のタイル
        var result = confirm('<move>でよろしいですか？ \n <remove>ならキャンセルを押してください');
        if(result) {
            actions = 'move';
        } else {
            acitons = 'remove';
        }
    }
    return actions;
}

function postForm(position, action, domain) {
 
    var form = document.createElement('form');
    var request = document.createElement('input');
 
    form.method = 'POST';
    form.action = domain;
 
    request.type = 'hidden'; //入力フォームが表示されないように
    request.name = 'text';
    value = {
        'next_pos': position,
        'motion': action,
                    };
    var json = JSON.stringify(value);
    request.value = json;
    //request.value = position;
    console.log(request);

    form.appendChild(request);
    console.log(form)
    document.body.appendChild(form);
 
    form.submit();
 
}