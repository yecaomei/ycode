function fnFormatDetails ( oTable, nTr )
{
    var aData = oTable.fnGetData( nTr );
    var sOut = '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">';
    sOut += '<tr><td>前置条件:</td><td>'+aData[10]+'</td></tr>';
    sOut += '<tr><td>操作步骤:</td><td>'+aData[11]+'</td></tr>';
    sOut += '<tr><td>页面逻辑结果:</td><td>'+aData[12]+'</td></tr>';
    sOut += '<tr><td>数据库结果:</td><td>'+aData[13]+'</td></tr>';
    sOut += '<tr><td>用例级别:</td><td>'+aData[14]+'</td></tr>';
    sOut += '<tr><td>所属版本:</td><td>'+aData[15]+'</td></tr>';
    sOut += '<tr><td>用例描述:</td><td>'+aData[16]+'</td></tr>';
    sOut += '<tr><td>创建时间:</td><td>'+aData[17]+'</td></tr>';
    sOut += '<tr><td>最后修改人:</td><td>'+aData[18]+'</td></tr>';
    sOut += '</table>';

    return sOut;
}

$(document).ready(function() {

    $('#dynamic-table').dataTable( {
        "aaSorting": [[ 0, "desc" ]]
    } );

    /*
     * Insert a 'details' column to the table
     */
    var nCloneTh = document.createElement( 'th' );
    var nCloneTd = document.createElement( 'td' );
    nCloneTd.innerHTML = '<img src="/images/details_open.png">';
    nCloneTd.className = "center";

    $('#hidden-table-info thead tr').each( function () {
        this.insertBefore( nCloneTh, this.childNodes[0] );
    } );

    $('#hidden-table-info tbody tr').each( function () {
        this.insertBefore(  nCloneTd.cloneNode( true ), this.childNodes[0] );
    } );

    /*
     * Initialse DataTables, with no sorting on the 'details' column
     */
    var oTable = $('#hidden-table-info').dataTable( {
        "aoColumnDefs": [
            { "bSortable": false, "aTargets": [ 0 ] }
        ],
        "aaSorting": [[1, 'desc']]
    });

    /* Add event listener for opening and closing details
     * Note that the indicator for showing which row is open is not controlled by DataTables,
     * rather it is done here
     */
    $(document).on('click','#hidden-table-info tbody td img',function () {
        var nTr = $(this).parents('tr')[0];
        if ( oTable.fnIsOpen(nTr) )
        {
            /* This row is already open - close it */
            this.src = "/images/details_open.png";
            oTable.fnClose( nTr );
        }
        else
        {
            /* Open this row */
            this.src = "/images/details_close.png";
            oTable.fnOpen( nTr, fnFormatDetails(oTable, nTr), 'details' );
        }
    } );
} );