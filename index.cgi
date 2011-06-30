#!/usr/bin/perl
use Mojolicious::Lite;
use utf8;
use DBI;
use Encode qw/encode decode/;

my $database = '/home/sqlitedb/testdb/testdb.db';
my $data_source = "dbi:SQLite:dbname=$database";
my $dbh = DBI->connect(
	$data_source,
	undef,
	undef,
	{
		RaiseError => 1,
		PrintError => 0,
		AutoCommit => 1,
	}
);

get '/' => sub {

	my $self = shift;

	my $sth = $dbh->prepare('select * from testtable');
	$sth->execute;

	my $dbdata = '';
	while (my $row = $sth->fetchrow_hashref){
		$dbdata = decode('UTF-8', $row->{data});
	}

	my $showDelForm = '';
	if ($dbdata) {
		$showDelForm = 1;
	}

	$dbh->disconnect;
	$self->render(dbdata => $dbdata, showDelForm => $showDelForm);

} => 'index';

post 'update' => sub {

	my $self = shift;
	my $params = $self->req->body_params->to_hash;
	my $data = $params->{data};

	my $sth = $dbh->prepare('select * from testtable');
	$sth->execute;

	my $dbdata = '';
	while (my $row = $sth->fetchrow_hashref){
		$dbdata = decode('UTF-8', $row->{data});
	}

	my $sql = '';
	if ($dbdata) {
		$sql = "update testtable set data=?";
	}else {
		$sql = "insert into testtable (data) values (?);";
        }

	$sth = $dbh->prepare($sql);
	$dbh->begin_work;
	$sth->execute($data);

	if ($@) {
		$dbh->rollback;
	}else {
		$dbh->commit;
	}

	$dbh->disconnect;
	return $self->redirect_to('index');
};

post 'delete' => sub {

        my $self = shift;
        my $params = $self->req->body_params->to_hash;

        my $sth = $dbh->prepare('select * from testtable');
        $sth->execute;

        my $dbdata = '';
        while (my $row = $sth->fetchrow_hashref){
                $dbdata = decode('UTF-8', $row->{data});
        }

        my $sql = '';
        if ($dbdata) {
		$sql = "delete from testtable";
		$sth = $dbh->prepare($sql);
		$dbh->begin_work;
		$sth->execute();

		if ($@) {
			$dbh->rollback;
		}else {
			$dbh->commit;
		}
	}

        $dbh->disconnect;
        return $self->redirect_to('index');
}; 

app->secret('mojolisicouslite+sqlite');
app->start;

__DATA__

@@ index.html.ep
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<head><title>Mojolicious::lite + sqlite フォームサンプル</title></head>
<html>
<body>
<h1>Mojolicious::lite + sqlite を使ったフォームサンプル</h1>
<ul>
<li>
<form method="post" action="<%= url_for('update') %>">
データ : <input type="text" name="data" value="<%= $dbdata %>">
<input type="submit" value="登録/更新する">
</form>
</li>
</ul>
<% if ($showDelForm) { %>
<p>登録されたデータがあります</p>
<form method="post" action="<%= url_for('delete') %>">
<input type="submit" value="データを削除">
<% }else{ %>
<p>登録されたデータはありません</p>
<% } %>
</body>
</html>
