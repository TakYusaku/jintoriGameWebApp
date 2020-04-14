$(function() {
    $.get('http://localhost:8002/play_page/game_start')
    .done(function(data) {
        document.getElementById('num_turn').innerHTML = data['turn'];
        console.log(data)
        makeField(data);
        makePointTable(data);
    });
});
function makePointTable(data){
    var parents = document.getElementById('point_table');
    var table_id = document.getElementById('point_id1');
    var heder_list = [' ','tile','area','total']
    var index_list = ['player','com']
    if(table_id!=null){
        parents.removeChild(table_id);
    }
    var tableJs = document.createElement('table');
    tableJs.id = 'point_id1';
    for(i = 0; i < 3; i++){
        var trJs = document.createElement('tr');
        for(j = 0; j < 4; j++){
            if(i==0){
                var tdJs = document.createElement('th');
                tdJs.innerHTML = heder_list[j];
            }else{
                var tdJs = document.createElement('td');
                if(j==0){
                    tdJs.innerHTML = index_list[i-1];
                }else{
                    if(i==2){
                        tdJs.innerHTML = data['now_point'][j+2];
                    }else{
                        tdJs.innerHTML = data['now_point'][j-1];
                    }
                }
            }
            trJs.appendChild(tdJs);
        }
        tableJs.appendChild(trJs);
    }
    parents.appendChild(tableJs);
    console.log('after_parents',parents)
}

function makeField(data){
    pf = data['pf'];
    uf = data['uf'];
    console.log('updated')
    var parents = document.getElementById('field');
    console.log('parents',parents)
    //var bodyJs = document.body;
    var table_id = document.getElementById('table_id1');
    console.log('before_table_id',table_id)
    if(table_id!=null){
        console.log('exist')
        parents.removeChild(table_id);
    }else{
        console.log('null')
    }
    //console.log('bodyJs',bodyJs)
    console.log('after_table_id',table_id);

    var tableJs = document.createElement('table');
    console.log('tableJs',tableJs)
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

    //var bodyJs = document.body;
    //console.log('bodyJs',bodyJs)
    //bodyJs.appendChild(tableJs);
    parents.appendChild(tableJs);
    console.log('after_parents',parents)
    document.getElementById('now_turn').innerHTML = data['now_turn'];
}

function sendAction(Cell){
    var rowNum = Cell.parentNode.rowIndex; // 行位置
    var cellNum = Cell.cellIndex; // 列位置
    var cellCol = Cell.style.backgroundColor; // セルの背景色
    console.log('cellCol',cellCol)
    //console.log(rowNum)
    //console.log(cellNum)
    //console.log(cellCol)

    var action = judgeAction(cellCol);
    //console.log(action)
    // var domain = 'http://localhost:8002/play/move';
    //postForm([cellNum, rowNum], action, domain)
    ajax_post([cellNum, rowNum], action)

}
function judgeAction(colors){
    var actions='remove';
    if(colors=='rgb(255, 255, 255)' || colors=='#ffffff'){ // 選択したタイルの色が白
        actions = 'move';
    } else if(colors=='#ff1493' || colors=='rgb(255, 20, 147)'){ // 選択したタイルが自分がいる位置
        actions = 'move';
    } else if(colors=='#00bfff' || colors=='rgb(0, 191, 255)'){ // 選択したタイルが相手エージェントのいる位置
        actions = 'remove';
    } else if(colors=='#add8e6' || colors=='rgb(173, 216, 230)'){ // 選択したタイルが相手エージェントのタイル
        actions = 'remove';
    } else if(colors=='#ffb6C1' || colors=='rgb(255, 182, 193)'){ // 選択したタイルが自分のタイル
        var result = confirm('<move>でよろしいですか？ \n <remove>ならキャンセルを押してください');
        if(result) {
            console.log('move')
            actions = 'move';
        } else{
            console.log('remove')
            acitons = 'remove';
        }
    }
    console.log('actions',actions);
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

function ajax_post(position, action) {
    value = {
        'next_pos': position,
        'motion': action,
                    };
    var Data = JSON.stringify(value);
    console.log('ajax_post')
    console.log(Data)
    $.ajax({
      type:'POST',
      url:'http://localhost:8002/play_page/game_action',
      //url:'http://localhost:8002/move',
      data:Data,
      contentType:'application/json',
      success:function(data) {
        //var result = JSON.parse(data.ResultSet).result;
        console.log('data[0]',data)
        console.log('data[pf]',data['pf'])
        if(data['code']==-1 || data['code']==-2){
            alert('無効な入力です');
        }
        makeField(data);
        makePointTable(data);
      }
    });
}