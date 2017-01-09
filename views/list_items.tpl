% rebase('page.tpl')
%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<h1>Buttons</h1>
<div class="table-responsive">
<table class="table">
%for item in items:
  <tr>
    <td>{{ item['label'] }}</td>
    <td><a href="{{ item['push-url'] }}">push</a></td>
    <td><a href="{{ item['delete-url'] }}">delete room</a></td>
    <td><a href="{{ item['initialise-url'] }}">initialise room</a></td>
  </tr>
%end
</table>
</div>
