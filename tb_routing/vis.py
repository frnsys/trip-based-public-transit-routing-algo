# Visualization tools, mostly useful for debugging

import itertools as it, operator as op, functools as ft
from collections import defaultdict

from . import utils as u, types as t


print_fmt = lambda tpl, *a, file=None, end='\n', **k:\
	print(tpl.format(*a,**k), file=file, end=end)

dot_str = lambda n: '"{}"'.format(n.replace('"', '\\"'))
dot_html = lambda n: '<{}>'.format(n)


def dot_for_lines(lines, dst):
	p = ft.partial(print_fmt, file=dst)

	stop_names, stop_edges = defaultdict(set), defaultdict(set)
	for line in lines:
		stop_prev = None
		for n, stop in enumerate(line.stops):
			stop_names[stop].add('{}[{}]'.format(line.id, n))
			if stop_prev: stop_edges[stop_prev].add(stop)
			stop_prev = stop

	p('digraph {{')

	p('\n  ### Labels')
	for stop, line_names in stop_names.items():
		label = '<b>{}</b>{}'.format(
			stop.name, '<br/>- '.join([''] + sorted(line_names)) )
		name = stop_names[stop] = 'stop-{}'.format(stop.id)
		p('  {} [label={}]'.format(dot_str(name), dot_html(label)))

	p('\n  ### Edges')
	for stop_src, edges in stop_edges.items():
		name_src = stop_names[stop_src]
		for stop_dst in edges:
			name_dst = stop_names[stop_dst]
			p('  {} -> {}', *map(dot_str, [name_src, name_dst]))
	p('}}')


def dot_for_tp_subtree(subtree, dst):
	assert subtree.prefix, 'Only subtrees are proper graphs'

	p = ft.partial(print_fmt, file=dst)
	def node_name(node):
		v = node.value
		if isinstance(v, t.public.Stop): v = v.name
		elif isinstance(v, t.base.LineStop):
			v = '{}:{:x}[{}]'.format(node.seed, v.line.id, v.stopidx)
		else: raise ValueError(type(v), v)
		return v

	p('digraph {{')

	stops_src, stops_dst = set(), set()
	for k, node_src_set in subtree.tree.items():
		for node_seed, node_src in node_src_set.items():
			name_src = node_name(node_src)
			if isinstance(node_src.value, t.public.Stop):
				if node_src.edges_to: stops_src.add(name_src)
				else: stops_dst.add(name_src)
			for node_dst in node_src.edges_to:
				name_dst = node_name(node_dst)
				p('  {} -> {}', *map(dot_str, [name_src, name_dst]))

	for subset in filter(None, [stops_src, stops_dst]):
		p( 'subgraph {{\n  rank = same;{};\n}}',
			', '.join(map(dot_str, sorted(subset))) )

	p('}}')
