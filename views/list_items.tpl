% rebase('page.tpl')
%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<h1>Buttons</h1>
<div class="table-responsive">
<table class="table">
%for item in items:
  <tr>
    <td>{{ item['label'] }}</td>
    <td><a href="/{{ item['push-url'] }}">push</a></td>
    <td><a href="/delete/{{ item['delete-url'] }}">delete</a></td>
    <td><a href="/initialise/{{ item['initialise-url'] }}">initialise</a></td>
  </tr>
%end
</table>
</div>
