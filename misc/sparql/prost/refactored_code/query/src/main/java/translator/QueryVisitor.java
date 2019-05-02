package translator;

import java.util.ArrayList;
import java.util.List;

import org.apache.jena.shared.PrefixMapping;
import org.apache.jena.sparql.algebra.OpVisitorBase;
import org.apache.jena.sparql.algebra.op.OpBGP;
import org.apache.jena.sparql.algebra.op.OpFilter;
import org.apache.jena.sparql.algebra.op.OpLeftJoin;
import org.apache.jena.sparql.algebra.op.OpProject;
import org.apache.jena.sparql.core.Var;
import org.apache.jena.sparql.expr.Expr;

public class QueryVisitor extends OpVisitorBase {

	private QueryTree mainQueryTree;
	private List<QueryTree> optionalQueryTrees;
	private List<Var> projectionVariables;
	private PrefixMapping prefixes;

	public QueryVisitor(PrefixMapping prefixes) {
		super();
		this.prefixes = prefixes;
		this.optionalQueryTrees = new ArrayList<>();
	}

	public List<Var> getProjectionVariables() {
		return this.projectionVariables;
	}

	public List<QueryTree> getOptionalQueryTrees() {
		return this.optionalQueryTrees;
	}

	public QueryTree getMainQueryTree() {
		return this.mainQueryTree;
	}

	public void visit(OpBGP opBGP) {
		this.mainQueryTree = new QueryTree(opBGP.getPattern().getList());
	}
	
	public void visit(OpBGP opBGP, boolean isOptional, String filter) {
		if (!isOptional) {
			// main join tree triples
			this.mainQueryTree = new QueryTree(opBGP.getPattern().getList());
		} else {
			// optional triples
			this.optionalQueryTrees.add(new QueryTree(opBGP.getPattern().getList(), filter));
		}
	}

	public void visit(OpLeftJoin opLeftJoin) {
		if (opLeftJoin.getLeft() instanceof OpBGP) {
			this.visit((OpBGP) opLeftJoin.getLeft(), false, null);
		}
		// set optional triples
		if (opLeftJoin.getRight() instanceof OpBGP) {
			// filter expression for the optional
			if (opLeftJoin.getExprs() != null) {
				FilterVisitor filterVisitor = new FilterVisitor(this.prefixes);
				for (Expr e : opLeftJoin.getExprs()) {
					e.visit(filterVisitor);
				}
				String optionalFilter = filterVisitor.getSQLFilter();
				this.visit((OpBGP) opLeftJoin.getRight(), true, optionalFilter);
			} else {
				this.visit((OpBGP) opLeftJoin.getRight(), true, null);
			}
		}
	}

	public void visit(OpFilter opFilter) {
		FilterVisitor filterVisitor = new FilterVisitor(this.prefixes);
		for (Expr e : opFilter.getExprs()) {
			e.visit(filterVisitor);
		}
		this.mainQueryTree.setFilter(filterVisitor.getSQLFilter());
	}

	public void visit(OpProject opProject) {
		this.projectionVariables = opProject.getVars();
	}
}
